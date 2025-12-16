import os

import pandas as pd
import math
import plotly.graph_objects as go

from ..shop_runner import ShopSession
from .model_builder import AttributeBuilderObject


def simple_model(plant_orig: AttributeBuilderObject) ->ShopSession:

    # Define h_max and h_min such that they cover the gross head range given in the turb_eff_curves
    h_min = 10000
    h_max = 0
    plant_q_max = 0.0
    for g in plant_orig.generators:
        eff_curves = g.turb_eff_curves.get()

        if eff_curves is None:
            eff_curves = []
            for n in g.needle_combinations:
                n_eff_curves = n.turb_eff_curves.get()
                eff_curves += n_eff_curves
        
        gen_q_max = 0.0
        for curve in eff_curves:
            h_min = min(h_min,curve.name)
            h_max = max(h_max,curve.name)
            gen_q_max = max(gen_q_max,curve.index[-1]) 

        plant_q_max += gen_q_max

    ## lrl and hrl must be integers to be able to divide into sections of 10 cm
    h_max = math.ceil(h_max)
    h_min = max(math.floor(h_min), 1)
    
    # Define the number of timesteps equal to the number of 10 cm in the max gross head
    n_heights = 10*(h_max - h_min) 
    shop = ShopSession()
    starttime = pd.Timestamp("1-1-2023") ## Random starttime
    shop.set_time_resolution(starttime=starttime, endtime=starttime+pd.Timedelta(hours=n_heights),timeunit="hour")

    # Define reservoir with the calculated lrl and hrl
    rsv = shop.model.reservoir.add_object("rsv")
    rsv.lrl.set(h_min)
    rsv.hrl.set(h_max)
    # Assuming linear vol-head curve, define max volume such that when the generators run at max discharge, the gross head is reduced by 10 cm in each timestep
    rsv.max_vol.set(plant_q_max *3600/10**6 * n_heights)
    # Define linear vol-head curve
    rsv.vol_head.set(pd.Series([rsv.lrl.get(),rsv.hrl.get()],index=[0,rsv.max_vol.get()]))

    # Define plant with the original properties, except outline line equal to zero since we have no downstream reservoir
    plant = shop.model.plant.add_object(plant_orig.get_name())
    plant.outlet_line.set(0.0)
    plant.main_loss.set(plant_orig.main_loss.get())
    plant.penstock_loss.set(plant_orig.penstock_loss.get())

    rsv.connect_to(plant)

    # Define generators with the original properties
    for gen_orig in plant_orig.generators:

        gen = shop.model.generator.add_object(gen_orig.get_name())
        gen.p_min.set(gen_orig.p_min.get())
        gen.p_max.set(gen_orig.p_max.get())
        gen.penstock.set(gen_orig.penstock.get())
        gen.gen_eff_curve.set(gen_orig.gen_eff_curve.get())
        turb_eff_curves = gen_orig.turb_eff_curves.get()
        if turb_eff_curves is not None:
            gen.turb_eff_curves.set(turb_eff_curves)

        gen.connect_to(plant)

        for needle_orig in gen_orig.needle_combinations:
            needle = shop.model.needle_combination.add_object(needle_orig.get_name())
            needle.p_min.set(needle_orig.p_min.get())
            needle.p_max.set(needle_orig.p_max.get())
            needle.turb_eff_curves.set(needle_orig.turb_eff_curves.get())

            needle.connect_to(gen)

    # Define bypass river, in case the discharge through the plant is not sufficient for following the reservoir schedule
    river = shop.model.river.add_object("river")
    river.upstream_elevation.set(rsv.lrl.get())
    river.flow_cost.set(1000)

    rsv.connect_to(river)

    # Define prices such that the generators produce at max discharge
    market = shop.model.market.add_object("market")
    market.sale_price.set(10)
    market.max_sale.set(10000)
    rsv.energy_value_input.set(9)

    # Define reservoir schedule such that the gross head starts at max, is reduced by 10 cm every timestep, and ends at min
    rsv.start_head.set(h_max)
    rsv.schedule.set(pd.Series([rsv.max_vol.get() - i*rsv.max_vol.get()/(n_heights) for i in range(n_heights+1)], index=[starttime+pd.Timedelta(hours=i) for i in range(n_heights+1)]))
    rsv.schedule_flag.set(pd.Series([2,1], index=[starttime,starttime+pd.Timedelta(hours=n_heights)]))

    return shop


def generate_combinations(elements: list) ->list:
        
        # This function produced the power set of a list of elements, excluding the empty set.
        # The idea is to represent each combination of list elements as a binary number of length equal to the number of elements.
        # Whether or not the nth list element is included in the combination is represented by the nth digit in the binary number.
        # In this way, we can retrieve all the 2**number_of_elements combinations by looping through all binary numbers between 1 and 2**number_of_elements.

        number_of_elements = len(elements)
        combination_list = []
            
        for i in range(1, 2**number_of_elements):
            combination = []
            binary = bin(i)[2:]
            binary = "0"*(number_of_elements-len(binary)) + binary
                
            for j in range(0, number_of_elements):
                if binary[j] == "1":
                    combination.append(elements[j])
                
            combination_list.append(combination)
            
        return combination_list


def create_pq_curves(plant_name: str, shop: ShopSession, pq_type: str, filepath: str, produce_plot: bool):

    if pq_type != "original" and pq_type != "convex":
         raise ValueError('Invalid pq_type. The pq_type must be either "original" or "convex".')
    
    if plant_name not in shop.model.plant.get_object_names():
        raise ValueError('The given plant does not exist in the given shop model.')

    # Create folder to store the resulting files
    plant_folder = filepath + "\\" + plant_name + "_" + pq_type
    if not os.path.isdir(plant_folder):
        os.mkdir(plant_folder)

    # Generate all possible combinations of which generators are operating
    plant_original = shop.model.plant[plant_name]
    generators = plant_original.generators
    generator_names = [gen.get_name() for gen in generators]
    combination_list = generate_combinations(generator_names)

    for combination in combination_list:

        # For each of the combinations, create a new shop session
        
        ## Use simple_model to define the shop model such that the generators run continuosly for the entire operational range
        shop = simple_model(plant_original)

        plant_new = shop.model.plant[plant_name]
        generators = plant_new.generators

        ## The generators in the combination are committed to run, and the others are on maintenance
        committed = []
        for gen in generators:
            if gen.get_name() in combination:
                committed.append(gen)
                gen.committed_in.set(1)
            else:
                gen.maintenance_flag.set(1)

        ## Run shop, and remeber to retrieve the pq_curves
        shop.save_pq_curves("on",[])
        shop.set_mip_nseg("all",20)
        shop.set_nseg("all",20)
        shop.start_sim([],3)
        shop.set_code("incremental",[])
        shop.start_sim([],5)

        # Given the pq curves and gross heads from the shop run, create dataframes, csv files and plots of pq curves and pqh surfaces

        ## Retrive the gross head
        gross_head_list = plant_new.gross_head.get()
        
        timesteps = len(gross_head_list)
        
        ## Since each generator has its own pq curves and net heads, loop through all committed generators
        for gen in committed:

            ### Retrieve the pq curves of the desired type
            if pq_type == "original":
                pq = gen.original_pq_curves.get()
            elif pq_type == "convex":
                pq = gen.convex_pq_curves.get()
                
            if pq is None:
                pq = []
                for needle_comb in gen.needle_combinations:
                    if pq_type == "original":
                        needle_pq = needle_comb.original_pq_curves.get()
                    elif pq_type == "convex":
                        needle_pq = needle_comb.convex_pq_curves.get()
                
                    if needle_pq is not None:
                        pq += needle_pq   
            
            ### These lists will finally constitute the columns in the dataframes of pq curves and pqh surfaces
            curve_indices = []
            all_q = []
            all_p = []
            all_head = []

            ### Retrieve the loss factors in the tunnels, needed to compute the net head
            main_loss = plant_new.main_loss.get()[0]
            try:
                penstock_loss = plant_new.penstock_loss.get()[0]
            except:
                penstock_loss = 0
            penstock_number = gen.penstock.get()

            ### Initialise the plots, if a plot is requested
            if produce_plot:
                fig_2D = go.Figure(data = go.Scatter(x = [], y = []))
                fig_3D = go.Figure(data = go.Scatter3d(x = [], y = [], z = []))

            ### In order to keep track of which curve a pair of p and q belong to, loop through the pq curves
            for i,curve in enumerate(pq):
                
                #### Index to keep track of which curve p and q belong to
                curve_indices += [i]*len(curve)

                #### Retrieve all p and q in this curve
                curve_q = curve.index
                curve_p = curve.values

                #### Retrieve the gross head at the same timestep as the pq curve
                gross_head = gross_head_list.values[i]

                #### Compute the net head from the gross head for each q on the curve, and assume that the discharges to the other generators is the running discharge
                head_list = []
                main_discharge_other_gen = 0
                penstock_discharge_other_gen = 0

                for other_gen in committed:
                    if other_gen != gen:
                        other_gen_discharge = other_gen.discharge.get().iloc[i]
                        main_discharge_other_gen +=other_gen_discharge
                        if other_gen.penstock.get() == penstock_number:
                            penstock_discharge_other_gen += other_gen_discharge
                                
                for discharge in curve_q:
                    main_discharge = main_discharge_other_gen + discharge
                    penstock_discharge = penstock_discharge_other_gen + discharge
                    head = gross_head - main_loss*main_discharge**2 - penstock_loss*penstock_discharge**2
                    head_list.append(head)
                    
                all_q += list(curve_q)
                all_p += list(curve_p)
                all_head += head_list


                #### Add the curve as a trace in the plots, if a plot is requested
                if produce_plot:
                    red = 255 - 255/timesteps*i
                    blue = 255/timesteps*i
                    trace_color = "rgb(" + str(red) + ",0," + str(blue) + ")"
                    
                    fig_2D.add_scatter(x = curve_q, y = curve_p,
                        showlegend=False,
                        marker=dict(
                            size=2,
                            color=trace_color),
                        line=dict(
                            color=trace_color))

                    fig_3D.add_scatter3d(x = curve_q, y = head_list, z = curve_p,
                        showlegend=False,
                        marker=dict(
                            size=2,
                            color=trace_color),
                        line=dict(
                            color=trace_color))
            
            ### Save pq curves and pqh surface as csv files
            gen_name = gen.get_name()
            combination_name = ""
            for any_gen_name in combination:
                combination_name += any_gen_name[-1]

            df_pq = pd.DataFrame()
            df_pq["Curve index"] = curve_indices
            df_pq["Discharge"] = all_q
            df_pq["Power"] = all_p
            df_pq.to_csv(plant_folder + "\\pq_" + gen_name + "_" + combination_name + "_" + pq_type + ".csv",sep=";",index=False)       
                
            df_pqh = pd.DataFrame()
            df_pq["Curve index"] = curve_indices
            df_pqh["Discharge"] = all_q
            df_pqh["Head"] = all_head
            df_pqh["Power"] = all_p
            df_pqh.to_csv(plant_folder + "\\pqh_" + gen_name + "_" + combination_name + "_" + pq_type + ".csv",sep=";",index=False)
            
            ### Save plot of pq curves and pqh surface as png or html, resepcitvely, if plot is requested
            if produce_plot:
                fig_2D.update_layout(
                    xaxis_title = "Discharge (m^3/s)",
                    yaxis_title = "Power (MW)",
                    title=dict(
                    text="PQ curves of " + gen_name + " in combination [" + combination_name + "]"))
                fig_2D.write_image(plant_folder + "\\pq_" + gen_name + "_" + combination_name + "_" + pq_type + ".png")

                fig_3D.update_layout(
                    scene=dict(
                    xaxis_title = "Discharge (m^3/s)",
                    yaxis_title = "Head (m)",
                    zaxis_title = "Power (MW)"),
                    title=dict(
                    text="PQH surface of " + gen_name + " in combination [" + combination_name + "]"))
                fig_3D.write_html(plant_folder + "\\pqh_" + gen_name + "_" + combination_name + "_" + pq_type + ".html")
