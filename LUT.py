##################################################################
#   R E A D M E
##################################################################
'''
Methods to launch this script:
- from command line
  - three main parameters: -i, -o, -l
  -i specifies the input file
    - if -i is not used, all files in the current directory and all subdirectories (except _LUTs and _OUTPUT folders) will be used
  -o specifies where to output
    - if -o is not used, the output file path will automatically be the same as the input, under the _OUTPUT folder
  -l specifies the LUT used (from _LUTs folder)
    - if -l is not used, lut-day.png is used

version 1.0
2019-11-08

'''

import argparse
import sys
import os
import math
from PIL import Image

def load_lut(lut_filename):
  global lut_3d
  lut_3d = {} 
  # read the LUT image
  if os.path.isfile(lut_filename) == False:
    lut_path = os.path.join('_LUTs', lut_filename)
    lut = Image.open(lut_path)
  else:
    lut = Image.open(lut_filename)
    
  # populate the LUT dictionary
  n = 0
  for y in range(0, lut.height):
    for x in range(0, lut.width):
      x_local = x%16
      z = math.floor(x/16)
      coord = (x_local, y, z)
      lut_3d[str(coord)] = lut.getpixel( (x, y) )
      #print(x,y,':',lut.getpixel((x,y)))
      n+=1

  # print the LUT dictionary (debug)
  '''
  i = 0
  for t in lut_3d.items():
    zz = math.floor(i/(16*16))
    print(zz, i, t)
    i+=1
  '''

def lerp_color(color1, color2, factor):
  output_R = color1[0] + ( (color2[0] - color1[0]) * factor)
  output_G = color1[1] + ( (color2[1] - color1[1]) * factor)
  output_B = color1[2] + ( (color2[2] - color1[2]) * factor)
  return (output_R, output_G, output_B)

def lerp_plane(r_min, r_max, g_min, g_max, b, input):
  i00 = (r_min, g_min, b)
  i01 = (r_max, g_min, b)

  i10 = (r_min, g_max, b)
  i11 = (r_max, g_max, b)
  
  lut00 = lut_3d[str(i00)]
  lut01 = lut_3d[str(i01)]
  lut10 = lut_3d[str(i10)]
  lut11 = lut_3d[str(i11)]
  
  R_interpolate = ( input[0] - (r_min*17) )/17
  G_interpolate = ( input[1] - (g_min*17) )/17

  c0 = lerp_color(lut00, lut01, R_interpolate)
  c1 = lerp_color(lut10, lut11, R_interpolate)
  return lerp_color(c0, c1, G_interpolate)

def process_image(input_image_path, output_image_path):
  input_img = Image.open(input_image_path)
  output_img = Image.new('RGBA', (input_img.width, input_img.height), color = (0,0,0,0))

  for y in range(0, input_img.height):
    for x in range(0, input_img.width):
      # get RGB of pixel

      if input_img.mode != 'RGBA':
        input_img = input_img.convert('RGBA')
      
      input_pix = input_img.getpixel( (x, y) )
      input_R = input_pix[0]
      input_G = input_pix[1]
      input_B = input_pix[2]
      alpha = input_pix[3]
      if alpha != 0:
        # find cage
        cage_R_min = math.floor( input_R/17 )
        cage_R_max = math.ceil(  input_R/17 )
        cage_G_min = math.floor( input_G/17 )
        cage_G_max = math.ceil(  input_G/17 ) 
        cage_B_min = math.floor( input_B/17 )
        cage_B_max = math.ceil(  input_B/17 )
        
        B_interpolate = ( input_B - (cage_B_min*17) )/17

        plane0 = lerp_plane(cage_R_min, cage_R_max, cage_G_min, cage_G_max, cage_B_min, input_pix)
        plane1 = lerp_plane(cage_R_min, cage_R_max, cage_G_min, cage_G_max, cage_B_max, input_pix)
        
        output = lerp_color(plane0, plane1, B_interpolate)
        output_RGBA = ( int(output[0]), int(output[1]), int(output[2]), alpha)

        # put pixel in output image
        output_img.putpixel( (x,y) , output_RGBA)

  # save output image
  output_folder = os.path.dirname(output_image_path)
  os.makedirs(output_folder, exist_ok = True)
  output_img.save(output_image_path)
  print('Saved', output_image_path)

def run(options):
  lut_filename = options['lut']  
  load_lut(lut_filename)

  dropped_instructions = sys.argv

  #input(sys.argv)
  if options['input'] == None:
    if os.path.realpath(__file__) in dropped_instructions:
      dropped_instructions.remove(os.path.realpath(__file__))
  else:
    dropped_instructions = options['input']

  if dropped_instructions != [] and dropped_instructions != '':
    print('Detected inputs:')
    print(dropped_instructions)
    # --------------------------------------------------------------------
    # the main run process
    input_filename = options['input']
    output_filename = options['output']
    
    if options['output'] == '':
      output_filename = os.path.join('_OUTPUT', input_filename)
    process_image(input_filename, output_filename)
  elif dropped_instructions == '':
    # walk through the directory and process all PNG files
    current_script_path = os.path.realpath(__file__)
    current_script_directory = os.path.dirname(current_script_path)
    print('script_directory:', current_script_directory)
    walked_instruction_list = []
    for root, dirs, files in os.walk(current_script_directory):
      for f in files:
        if '_LUTs' not in root:
          if '_OUTPUT' not in root:
            if f[-4:].lower() == '.png':
              walked_instruction_list.append( os.path.join(root, f) )
    
    for i in walked_instruction_list:
      input_path = i
      relative_input_path_i = i
      relative_input_path = relative_input_path_i.replace(current_script_directory, '')[1:]
      relative_output_path = os.path.join('_OUTPUT', relative_input_path)
      process_image(input_path, relative_output_path)
    print('Walked instructions detected:\n', walked_instruction_list)
  
  else:
    print('No input given.')

if __name__ == '__main__':
  if len(sys.argv) > 2:
    parser = argparse.ArgumentParser(description = 'Process some arguments.')
    parser.add_argument('-i','--input',
                        help='File to process.'
                        )
    parser.add_argument('-o','--output',
                        help='File to output.'
                        )
    parser.add_argument('-l','--lut',
                        help='Override which LUT file to use.'
                        )
    options = vars(parser.parse_args())
    default_values = [
      ('input', ''),
      ('output', ''),
      ('lut', 'lut-day.png')
    ]
    for name, def_value in default_values:
      if not options[name]:
        options[name] = def_value
  else:

    input_var = ''
    if len(sys.argv) > 1:
      input_var = sys.argv[1]
    options = {
      'input' : input_var,
      'output': '',
      'lut' : 'lut-day.png'
    }
  run(options)
