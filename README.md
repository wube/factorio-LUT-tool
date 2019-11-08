A tool which applies LUT colours to images.

Usage options:

  A. Process all images automatically
    - Copy the LUT.py and _LUTs folder into your mod directory
    - Launch LUT.py directly, without any arguments
    - ! ALL found *.PNG images in this directory and subdirectories will be converted
    - ! Outputs can be found in _OUTPUT folder.
    
  B. Process only selected images
    - Launch LUT.py with arguments
      -i specifies the input file
      -o specifies where to output
      -l specifies the LUT used (from _LUTs folder)      
      -if -i is not used, all files in the current directory and all subdirectories (except _LUTs and _OUTPUT) will be searched
      -if -o is not used, the output file path will automatically be the same as the input, under the _OUTPUT folder
      -if -l is not used, lut-day.png is used  
    example command:
      LUT.py -i nuclear_furnace.png -o _OUTPUT/nuclear_furnace.png -l lut-day.png
    
  C. Drag&drop a file on LUT.py
    - lut-day will be applied to the file.

Requires:
 Python 3.7+ (might work with lower versions, but I tested with 3.7)

You can find which images got which LUT applied in the vanilla_instructions directory.
