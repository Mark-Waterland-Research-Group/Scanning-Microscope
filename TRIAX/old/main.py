import sys
import time
import instruments
import datetime
import pandas as pd

import os
import math

DEBUGMODE = True

class progressbar:
    def __init__(self, start_value, end_value, step):
        self.counter = 0
        self.points = math.ceil((end_value - start_value) / step) + 1
    
    def count(self):
        self.counter = self.counter + 1
        self.show_bar()
    
    def show_bar(self):
        percentage = math.floor((self.counter / self.points) * 100)
        bar_num = math.floor(percentage / 5)
        sys.stdout.write('\r')
        sys.stdout.write('[' + '=' * bar_num + ' ' * (20 - bar_num) + ']'
                         + str(percentage) + '% ')
        if percentage != 100:
            sys.stdout.flush()

class swipe:
    def __init__(self, lambda_i, lambda_f, stepsize, data_label='Reading'):
        '''Swipes motor from "lambda_i" to "lambda_f" with steps of size
        "stepsize" and returns the measured data in a Pandas DataFrame.
        Param:
        lambda_i (int): Initial position in nm 300-1100nm
        lambda_f (int): Final position in nm 300-1100nm
        stepsize (int): Step size in nm 5-50nm
        data_label (str): Label for data column
        Returns:
        swipe_data (pandas.DataFrame): Measured data'''
        # Seleccionar valores con algún criterio
        if lambda_i < 300 or lambda_i > 1100 or lambda_f < 300 or lambda_f > 1100:
            print('Error: Values off limits. Swipe range: 300-1100nm')
            return
        
        if stepsize < 5 or stepsize > 50:
            print('Error: Stepsize has to be between 5-50nm')
            return
        
        lambda_i = instruments.nm_to_step(lambda_i)
        lambda_f = instruments.nm_to_step(lambda_f)
        stepsize = stepsize * 7
        
        if DEBUGMODE:
            print('i:', lambda_i, ' f:', lambda_f, ' step:', stepsize)
        
        wavelen = []
        reading = []
        print('Starting swipe...')
        progress = progressbar(lambda_i, lambda_f, stepsize)
        progress.show_bar()
        
        current_pos = triax.read_motor_pos(False)
        triax.move_motor(lambda_i - current_pos)
        current_pos = triax.read_motor_pos(False)
        
        if DEBUGMODE:
            triax.read_motor_pos()
        
        wavelen.append(instruments.step_to_nm(current_pos))
        progress.count()
        
        for i in range(lambda_i, lambda_f, stepsize):
            if i + stepsize > lambda_f:
                break
            
            triax.move_motor(stepsize)
            current_pos = triax.read_motor_pos(False)
            
            if DEBUGMODE:
                print('Expected:', i + stepsize, '. Real:', current_pos)
            
            wavelen.append(instruments.step_to_nm(current_pos))
            progress.count()
        
        current_pos = triax.read_motor_pos(False)
        
        if current_pos < lambda_f:
            triax.move_motor(lambda_f - current_pos)
            current_pos = triax.read_motor_pos(False)
            
        wavelen.append(instruments.step_to_nm(current_pos))
        progress.count()
        
        if DEBUGMODE:
            print('Expected:', i + stepsize, '. Real:', triax.read_motor_pos(False))
        
        print('Swipe completed!')
        
        # Create a Pandas dataframe from the data.
        df = pd.DataFrame({'Wavelength(nm)': wavelen, data_label: reading})
        return df

def export_to_excel(df, sample_name, requested_name=''):
    '''Creates an excel with the DataFrame data presented and plotted.
    DataFrame must have 3 columns for: wavelength, reference_data, data.
    Param:
    df (pd.DataFrame): Data Frame to export'''
    if DEBUGMODE:
        excel_name = 'Output_debug.xlsx'
    elif requested_name != '':
        excel_name = requested_name + '.xlsx'
    else:
        now = datetime.datetime.now()
        now = (now.strftime("%d") + '-' + now.strftime("%m") + '-'
               + now.strftime("%Y") + '_' + now.strftime("%H") + '-'
               + now.strftime("%M"))
        excel_name = sample_name.replace(" ", "_") + '_' + now + '.xlsx'
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('./../Output_data/' + excel_name, engine='xlsxwriter')
    
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Data', startrow=3)
    
    # Get the xlsxwriter objects from the dataframe writer object.
    workbook = writer.book
    sheet_data = writer.sheets['Data']
    
    # Formating
    scientific_format = workbook.add_format({'num_format': '0.00E+00'})
    decimal_format = workbook.add_format({'num_format': '0.00'})
    sheet_data.set_column(1, 1, 15)
    sheet_data.set_column(2, 2, 13, scientific_format)
    sheet_data.set_column(3, 3, 13, scientific_format)
    sheet_data.set_column(4, 4, 15, decimal_format)
    
    title_format = workbook.add_format({'bold': True, 'font_size': 20, 'font_color': 'navy'})
    subtitle_format = workbook.add_format({'bold': True, 'font_size': 14})
    subtitle2_format = workbook.add_format({'bold': True, 'font_size': 12})
    size12_format = workbook.add_format({'font_size': 12})
    
    sheet_data.write(0, 0, 'UPC', title_format)
    sheet_data.write(1, 0, 'TELECOM-BCN', subtitle_format)
    sheet_data.write(0, 2, 'MNT group', subtitle_format)
    sheet_data.write(1, 2, 'Spectrometre v1.0', subtitle_format)
    sheet_data.set_column(5, 5, 11, subtitle2_format)
    sheet_data.set_column(6, 6, 20, size12_format)
    sheet_data.write(0, 5, 'Sample:')
    sheet_data.write(0, 6, sample_name)
    sheet_data.write(1, 5, 'Date_time:')
    sheet_data.write(1, 6, now)
    sheet_data.write(0, 8, 'Developed by')
    sheet_data.write(1, 8, 'Sebastian Padilla Romero', size12_format)
    
    # CHARTS
    measurements_chart = workbook.add_chart({'type': 'line'})
    measurements_chart.add_series({
        'name': 'Reference',
        'categories': '=Data!$B$5:$B$' + str(5 + len(df)),
        'values': '=Data!$C$5:$C$' + str(5 + len(df)),
        'line': {'color': 'blue'},
    })
    measurements_chart.add_series({
        'name': 'Sample',
        'categories': '=Data!$B$5:$B$' + str(5 + len(df)),
        'values': '=Data!$D$5:$D$' + str(5 + len(df)),
        'line': {'color': 'green'},
    })
    measurements_chart.set_title({'name': 'Measurements'})
    measurements_chart.set_x_axis({'name': 'Wavelength (nm)'})
    measurements_chart.set_y_axis({'name': 'Signal (A)'})
    sheet_data.insert_chart('G4', measurements_chart)
    
    try:
        os.mkdir('./../Output_data/')  # creates output directory if it does not exist
    except OSError:
        pass
    
    writer.save()
    print('Data generated and exported to excel.')

def configuration():
    while True:
        print('\nCurrent configuration:')
        print("3 - Monochromator's entry slit opening (in steps):", triax.entry_slit_pos)
        print("4 - Monochromator's exit slit opening (in steps):", triax.exit_slit_pos)
        
        ans = input("Select parameter to adjust (by number) or press enter to quit: ")
        
        if not ans.isnumeric():
            break
        else:
            ans = int(ans)
            
            if ans < 3 or ans > 4:
                print('Incorrect selection')
                continue
            elif ans == 3:
                print("3 - Monochromator's entry slit opening")
                ans = int(input('Insert new opening (in steps): '))
                if not triax.move_entry_slit(ans):
                    continue
            elif ans == 4:
                print("4 - Monochromator's exit slit opening")
                ans = int(input('Insert new opening (in steps): '))
                if not triax.move_exit_slit(ans):
                    continue
            print('Parameter updated.')

# Main code
print('Welcome! Initializing instruments...')
triax = instruments.Triax()
triax.open()

ref_df = sample_df = output_df = lambda_i = lambda_f = stepsize = None

while True:
    ans = input("\nPress enter to start a new measure, send 'c' to go to parameter configuration, or send 'q' to quit\n")
    
    if ans == 'q':
        break
    elif ans == 'c':
        configuration()
        continue
    
    print('Introduce swipe parameters in nm:')
    lambda_i = int(input('Initial lambda (limits: 300-1100nm): '))
    lambda_f = int(input('Final lambda (limits: 300-1100nm): '))
    stepsize = int(input('Stepsize (limits: 5-50): '))
    
    print('Initial lambda:', lambda_i, 'nm. Final lambda:', lambda_f, 'nm. Stepsize:', stepsize, 'nm.')
    
    if lambda_i < 300 or lambda_i > 1100 or lambda_f < 300 or lambda_f > 1100 or stepsize < 5 or stepsize > 50:
        print('Error: Values off limits.')
        continue
    
    sample_name = input("\nIntroduce sample's name:")
    
    input('Reference swipe will be done. Remove the sample and press enter to continue.')
    ref_df = swipe(lambda_i, lambda_f, stepsize, 'Reference(A)')
    
    input('Sample swipe will be done. Place the sample and press enter to continue.')
    sample_df = swipe(lambda_i, lambda_f, stepsize, 'Sample(A)')
    
    output_df = pd.merge(ref_df, sample_df, on='Wavelength(nm)', how='outer')
    output_df['Transmission(%)'] = (sample_df['Sample(A)'] / ref_df['Reference(A)']) * 100
    
    ans = input("Enter a name for the excel file or press enter to use the default sample name-date-time format: ")
    export_to_excel(output_df, sample_name, ans)
    print('Measure completed. Restarting...')
    sample_df = output_df = lambda_i = lambda_f = stepsize = None

triax.close()
print('Quitting program... Bye!\n')
