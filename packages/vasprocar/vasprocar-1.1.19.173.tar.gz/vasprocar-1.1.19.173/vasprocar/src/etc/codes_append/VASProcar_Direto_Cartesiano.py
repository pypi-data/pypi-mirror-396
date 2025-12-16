# VASProcar Copyright (C) 2023
# GNU GPL-3.0 license


#=============================================================================
# Conversão do arquivo POSCAR/CONTCAR para coordenadas cartesianas/Diretas ===
#=============================================================================


#================
name_i = 'CONTCAR.vasp'
#---------------------------
poscar_i = open(name_i, "r")
for i in range(8): VTemp = poscar_i.readline()
poscar_i.close()
#------------------
string = str(VTemp)
if (string[0] == 'c' or string[0] == 'C'):  name_o = name_i.replace('.vasp','') + '_Direct.vasp'
if (string[0] == 'd' or string[0] == 'D'):  name_o = name_i.replace('.vasp','') + '_Cartesian.vasp'
#------------------------------------------------------------------------
poscar_i  = open(name_i, "r")
poscar_o  = open(name_o, "w")
VTemp = poscar_i.readline();  poscar_o.write(f'{VTemp}')
VTemp = poscar_i.readline();  poscar_o.write(f'{VTemp}');  param = float(VTemp)
VTemp = poscar_i.readline();  poscar_o.write(f'{VTemp}');  VTemp = VTemp.split();  A = [float(VTemp[0]), float(VTemp[1]), float(VTemp[2])]  
VTemp = poscar_i.readline();  poscar_o.write(f'{VTemp}');  VTemp = VTemp.split();  B = [float(VTemp[0]), float(VTemp[1]), float(VTemp[2])]
VTemp = poscar_i.readline();  poscar_o.write(f'{VTemp}');  VTemp = VTemp.split();  C = [float(VTemp[0]), float(VTemp[1]), float(VTemp[2])]
VTemp = poscar_i.readline();  poscar_o.write(f'{VTemp}')
VTemp = poscar_i.readline();  poscar_o.write(f'{VTemp}')
#-----------------------------------------------------
nions = 0;  VTemp = VTemp.split()
for k in range(len(VTemp)): nions += int(VTemp[k])
#-------------------------------------------------
VTemp = poscar_i.readline()
#--------------------------


#=========================================
if (string[0] == 'd' or string[0] == 'D'):
   #---------------------------
   poscar_o.write(f'Cartesian \n')
   #-----------------------------------------------------------
   # Escrita das coordenadas cartesianas ----------------------
   #-----------------------------------------------------------
   for k in range(nions):
       VTemp = poscar_i.readline().split()
       k1 = float(VTemp[0]); k2 = float(VTemp[1]); k3 = float(VTemp[2])
       coord_x = ((k1*A[0]) + (k2*B[0]) + (k3*C[0]))
       coord_y = ((k1*A[1]) + (k2*B[1]) + (k3*C[1]))
       coord_z = ((k1*A[2]) + (k2*B[2]) + (k3*C[2]))
       poscar_o.write(f'{coord_x} {coord_y} {coord_z} \n')
       #--------------------------------------------------


#=========================================
if (string[0] == 'c' or string[0] == 'C'):
   #---------------------------
   poscar_o.write(f'Direct \n')
   #--------------------------------------------------
   A1 = np.array([A[0]*param, A[1]*param, A[2]*param])
   A2 = np.array([B[0]*param, B[1]*param, B[2]*param])
   A3 = np.array([C[0]*param, C[1]*param, C[2]*param])
   #----------------------------------
   # Definir a matriz de transformação 
   T = np.linalg.inv(np.array([A1, A2, A3]).T)
   #---------------------------------------
   for k in range(nions):
       VTemp = poscar_i.readline().split()
       x = float(VTemp[0])
       y = float(VTemp[1])
       z = float(VTemp[2])      
       r = np.array([x, y, z]) # posição cartesiana dos átomos  
       #-----------------------------------------------------------
       # Escrita das coordenadas Diretas --------------------------
       #-----------------------------------------------------------
       f = np.dot(T, r)
       f = np.where(f < 0, f + 1, f)
       #------------------------------------
       if ((f[0] >= 0.0) and (f[0] <= 1.0)):
          if ((f[1] >= 0.0) and (f[1] <= 1.0)):
             if ((f[2] >= 0.0) and (f[2] <= 1.0)):
                for m in range(3):
                    f[m] = round(f[m], 6)
                    if (f[m] > 0.99999 or f[m] < 0.00001):
                       f[m] = 0.0
                poscar_o.write(f'{f[0]} {f[1]} {f[2]} {l} \n')


#---------------
poscar_i.close()   
poscar_o.close()
#---------------

"""
#=======================================================================

#-----------------------------------------------------------------
print(" ")
print("======================= Completed =======================")
print(" ")
#-----------------------------------------------------------------

#=======================================================================
# User option to perform another calculation or finished the code ======
#=======================================================================
if (len(inputs) == 0):
   execute_python_file(filename = '_loop.py')
"""
