# PyMLCA
## Software for Generalized Matrix-based LCA and Reliability Based LCA
#### Shinsuke Sakai   
 Emeritus Professor, The University of Tokyo, Japan   
 Visiting Professor, Yokohama National University, Japan

 ### Overview
This package provide the function for general-purpose matrix-based LCA analysis and LCA based on reliability design. Algorithm for sensitivity analysis using perturbation method is based on the theory shown by Sakai and Yokoyama[1]. 
Should any required packages be missing during execution, please install them accordingly. 

[1][Shinsuke Sakai and Koji Yokoyama. Formulation of sensitivity analysis in life cycle assessment using a
perturbation method. Clean technologies and environmental policy, Vol. 4, No. 2, pp. 72–78, 2002.](https://link.springer.com/article/10.1007/s10098-002-0150-2) 

### Procedure
1. Install this package using pip command.
1. Create a folder to store inventory data. As an example, the folder named 'SandwichPackage' is already created.
1. Save the inventory data to be analyzed in that folder.
1. Import PyMLCA module using 'from MLCArel import PyMLCA as pm' command.
1. Create an instance to manage the analysis using 'dp=pm.DesignProcess()' command.
1. From here on, use the created instance to perform the intended analysis.

### Operation check
The following describes the method for checking when using the inventory data in the SandwichPackage folder. Sample data for SandwichPackaged are provided in the [site](https://github.com/ShinsukeSakai0321/PyMLCA).

First, create an instance and define the inventory data folder.
```python
from MLCArel import PyMLCA as pm
dp=pm.DesignProcess()
path='./SandwichPackage'
dp.SetDfFromPath(path)
```
Next, perform a matrix-based LCA.
```python
solution,surplusFlow,loadValue=dp.SimpleAnalysis()
```
Confirm the created coefficient matrix.
```python
print(dp.rbld.mlca.coefficientMat)
```
The expected output would be as follows.
***
<table style="border-collapse: collapse;">
  <tr>
    <td style="border: none;"> mat</td>
    <td style="border: none;">production of aluminum</td>
    <td style="border: none;">production of aluminum foil</td>
    <td style="border: none;">production of electricity</td>
    <td style="border: none;">usage of aluminum foil</td>
  </tr>
  <tr>
    <td style="border: none;">aluminum </td>
    <td style="border: none;">1.0</td>
    <td style="border: none;">-1.0</td>
    <td style="border: none;">-0.01</td>
    <td style="border: none;">-0.0</td>
  </tr>
  <tr>
    <td style="border: none;">AluminumFoil </td>
    <td style="border: none;">0.0</td>
    <td style="border: none;">1.0</td>
    <td style="border: none;">0.00</td>
    <td style="border: none;">-1.0</td>
  </tr>
    <tr>
    <td style="border: none;">electricity </td>
    <td style="border: none;">-50.0</td>
    <td style="border: none;">-1.0</td>
    <td style="border: none;">1.00</td>
    <td style="border: none;">0.0</td>
  </tr>
    <tr>
    <td style="border: none;">SandwichPackages </td>
    <td style="border: none;">0.0</td>
    <td style="border: none;">0.0</td>
    <td style="border: none;">0.00</td>
    <td style="border: none;">1.0</td>
  </tr>
</table>

***
Display the solution of the process values.
```python
print(solution)
```
The expected output would be as follows. 
***   
[ 0.202  0.1   10.2    0.1  ]
***   
Display the names of the environmental impacts and their solutions.
```python
flowName,b,loadName=dp.GetName()
print('Names of the environmental impacts=',loadName)
print('Their solutions=',loadValue)
```
The expected output would be as follows. 
*** 
Names of the environmental impacts= ['SolidWaste', 'CO2']   
Their solutions= [22.52 30.6 ] 
***  
Calculation of sensitivity matrix.
```python
i=1
print('Calculation of sensitivity matrix for environmental load:',loadName[i])
print(dp.rbld.mlca.Smat(i))
```
The expected output would be as follows.   
***
Calculation of sensitivity matrix for environmental load: CO2   
[[-1.98039216  0.98039216  1.         -0.        ]   
 [-0.         -1.         -0.          1.        ]   
 [ 1.98039216  0.01960784 -2.         -0.        ]   
 [-0.         -0.         -0.         -1.        ]]   

***






