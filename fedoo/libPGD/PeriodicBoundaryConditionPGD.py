# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 15:27:43 2020

@author: Etienne
"""
# from fedoo.libProblem.ProblemBase   import ProblemBase 
from fedoo.libProblem.ProblemBase import BoundaryCondition
import numpy as np
from fedoo.libMesh.Mesh import MeshBase
from fedoo.libUtil.ModelingSpace import ModelingSpace

# def DefinePeriodicBoundaryConditionGrad(mesh, NodeCD, VarCD, dim='3D', tol=1e-8, ProblemID = 'MainProblem'):
#     """
#     Parameters
#     ----------
#     crd : mesh ID or mesh object
#         A periodic mesh to apply the periodic boundary conditions
#     NodeEps : lise of int
#         NodeCD is a list containing the node index of Grad displacement tensor component (virtual node)
#         In 2D: [[GradU_XX, GradU_XY],[GradU_YX, GradU_YY]]
#         In 3D: [[GradU_XX, GradU_XY, GradU_XZ],[GradU_YX, GradU_YY, GradU_YZ],[GradU_ZX, GradU_ZY, GradU_ZZ]]
#     VarEps : list of string
#         VarEps is a list containing the variable id used for each component
#     dim : '2D' or '3D', optional
#         This parameter is used to define if the periodicity is in 2D or in 3D.
#         A periodicity in 2D can be associated with a 3D mesh. 
#         The default is '2D'.
#     tol : float, optional
#         Tolerance for the position of nodes. The default is 1e-8.
#     ProblemID : ProblemID on which the boundary conditions are applied
#         The default is 'MainProblem'.

#     Returns
#     -------
#     None.

#     """
#     #TODO: add set to the mesh and don't compute the set if the set are already present
#     if dim in ['2D','2d']: dim = 2
#     if dim in ['3D','3d']: dim = 3

#     if isinstance(mesh, str): mesh = MeshBase.GetAll()[mesh]
#     crd = mesh.GetNodeCoordinates()
#     xmax = np.max(crd[:,0]) ; xmin = np.min(crd[:,0])
#     ymax = np.max(crd[:,1]) ; ymin = np.min(crd[:,1])
#     if dim == 3:                        
#         zmax = np.max(crd[:,2]) ; zmin = np.min(crd[:,2])
  
#     if dim == 2:                       
#         #Define node sets
#         left   = np.where( (np.abs(crd[:,0] - xmin) < tol) * (np.abs(crd[:,1] - ymin) > tol) * (np.abs(crd[:,1] - ymax) > tol))[0]
#         right  = np.where( (np.abs(crd[:,0] - xmax) < tol) * (np.abs(crd[:,1] - ymin) > tol) * (np.abs(crd[:,1] - ymax) > tol))[0]
#         bottom = np.where( (np.abs(crd[:,1] - ymin) < tol) * (np.abs(crd[:,0] - xmin) > tol) * (np.abs(crd[:,0] - xmax) > tol))[0]
#         top    = np.where( (np.abs(crd[:,1] - ymax) < tol) * (np.abs(crd[:,0] - xmin) > tol) * (np.abs(crd[:,0] - xmax) > tol))[0]
        
#         corner_lb = np.where((np.abs(crd[:,0] - xmin) < tol) * (np.abs(crd[:,1] - ymin) < tol))[0] #corner left bottom
#         corner_rb = np.where((np.abs(crd[:,0] - xmax) < tol) * (np.abs(crd[:,1] - ymin) < tol))[0] #corner right bottom
#         corner_lt = np.where((np.abs(crd[:,0] - xmin) < tol) * (np.abs(crd[:,1] - ymax) < tol))[0] #corner left top
#         corner_rt = np.where((np.abs(crd[:,0] - xmax) < tol) * (np.abs(crd[:,1] - ymax) < tol))[0] #corner right top

#         left = left[np.argsort(crd[left,1])]
#         right = right[np.argsort(crd[right,1])]
#         top = top[np.argsort(crd[top,0])]
#         bottom = bottom[np.argsort(crd[bottom,0])]
        
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0]], [np.full_like(right,1), np.full_like(left,  -1), np.full_like(right,-(xmax-xmin), dtype=float)], [right,left  ,np.full_like(right,NodeCD[0][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0]], [np.full_like(right,1), np.full_like(left,  -1), np.full_like(right,-(xmax-xmin), dtype=float)], [right,left  ,np.full_like(right,NodeCD[1][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1]], [np.full_like(top  ,1), np.full_like(bottom,-1), np.full_like(top  ,-(ymax-ymin), dtype=float)], [top  ,bottom,np.full_like(top  ,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1]], [np.full_like(top  ,1), np.full_like(bottom,-1), np.full_like(top  ,-(ymax-ymin), dtype=float)], [top  ,bottom,np.full_like(top  ,NodeCD[1][1])], ProblemID = ProblemID)
        
#         #elimination of DOF from edge left/top -> edge left/bottom
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1]], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1), np.full_like(corner_lt,-(ymax-ymin), dtype=float)], [corner_lt, corner_lb, np.full_like(corner_lt,NodeCD[1][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1]], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1), np.full_like(corner_lt,-(ymax-ymin), dtype=float)], [corner_lt, corner_lb, np.full_like(corner_lt,NodeCD[0][1])], ProblemID = ProblemID)
#         #elimination of DOF from edge right/bottom -> edge left/bottom
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0]], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1), np.full_like(corner_rb,-(xmax-xmin), dtype=float)], [corner_rb, corner_lb, np.full_like(corner_lt,NodeCD[0][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0]], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1), np.full_like(corner_rb,-(xmax-xmin), dtype=float)], [corner_rb, corner_lb, np.full_like(corner_lt,NodeCD[1][0])], ProblemID = ProblemID)
#         #elimination of DOF from edge right/top -> edge left/bottom
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0],VarCD[0][1]], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1), np.full_like(corner_rt,-(xmax-xmin), dtype=float), np.full_like(corner_rt,-(ymax-ymin), dtype=float)], [corner_rt, corner_lb, np.full_like(corner_rt,NodeCD[0][0]), np.full_like(corner_rt,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0],VarCD[1][1]], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1), np.full_like(corner_rt,-(xmax-xmin), dtype=float), np.full_like(corner_rt,-(ymax-ymin), dtype=float)], [corner_rt, corner_lb, np.full_like(corner_rt,NodeCD[1][0]), np.full_like(corner_rt,NodeCD[1][1])], ProblemID = ProblemID)                
                                       
#         #if rot DOF are used, apply continuity of the rotational dof on each oposite faces and corner
#         if 'RotZ' in ModelingSpace.ListVariable():
#             BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(right,1), np.full_like(left,-1)], [right,left], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(top,1), np.full_like(bottom,-1)], [top,bottom], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1)], [corner_lt, corner_lb], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1)], [corner_rb, corner_lb], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1)], [corner_rt, corner_lb], ProblemID = ProblemID)
#         if 'RotY' in ModelingSpace.ListVariable():
#             BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(right,1), np.full_like(left,-1)], [right,left], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(top,1), np.full_like(bottom,-1)], [top,bottom], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1)], [corner_lt, corner_lb], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1)], [corner_rb, corner_lb], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1)], [corner_rt, corner_lb], ProblemID = ProblemID)
#         if 'RotX' in ModelingSpace.ListVariable():
#             BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(right,1), np.full_like(left,-1)], [right,left], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(top,1), np.full_like(bottom,-1)], [top,bottom], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1)], [corner_lt, corner_lb], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1)], [corner_rb, corner_lb], ProblemID = ProblemID)
#             BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1)], [corner_rt, corner_lb], ProblemID = ProblemID)
        
#     elif dim == 3:                        
        
#         #Define node sets
#         left   = np.where( np.abs(crd[:,0] - xmin) < tol )[0]
#         right  = np.where( np.abs(crd[:,0] - xmax) < tol )[0]
#         bottom = np.where( np.abs(crd[:,1] - ymin) < tol )[0]
#         top    = np.where( np.abs(crd[:,1] - ymax) < tol )[0]
#         behind = np.where( np.abs(crd[:,2] - zmin) < tol )[0]
#         front  = np.where( np.abs(crd[:,2] - zmax) < tol )[0]
        
#         #extract edge from the intersection of faces
#         #l = left, r = right, b = bottom, t = top, f = front, d = behind
#         edge_lb = np.intersect1d(left , bottom, assume_unique=True)
#         edge_lt = np.intersect1d(left , top   , assume_unique=True)
#         edge_rb = np.intersect1d(right, bottom, assume_unique=True)
#         edge_rt = np.intersect1d(right, top   , assume_unique=True)
        
#         edge_bd = np.intersect1d(bottom, behind, assume_unique=True)
#         edge_bf = np.intersect1d(bottom, front , assume_unique=True)
#         edge_td = np.intersect1d(top   , behind, assume_unique=True)
#         edge_tf = np.intersect1d(top   , front , assume_unique=True)
        
#         edge_ld = np.intersect1d(left , behind, assume_unique=True)
#         edge_lf = np.intersect1d(left , front , assume_unique=True)
#         edge_rd = np.intersect1d(right, behind, assume_unique=True)
#         edge_rf = np.intersect1d(right, front , assume_unique=True)        
        
#         #extract corners from the intersection of edges
#         corner_lbd = np.intersect1d(edge_lb , edge_bd, assume_unique=True) 
#         corner_lbf = np.intersect1d(edge_lb , edge_bf, assume_unique=True)
#         corner_ltd = np.intersect1d(edge_lt , edge_td, assume_unique=True)
#         corner_ltf = np.intersect1d(edge_lt , edge_tf, assume_unique=True)
#         corner_rbd = np.intersect1d(edge_rb , edge_bd, assume_unique=True)
#         corner_rbf = np.intersect1d(edge_rb , edge_bf, assume_unique=True)
#         corner_rtd = np.intersect1d(edge_rt , edge_td, assume_unique=True)
#         corner_rtf = np.intersect1d(edge_rt , edge_tf, assume_unique=True)
        
#         all_corners = np.hstack((corner_lbd, corner_lbf, corner_ltd, corner_ltf, 
#                                  corner_rbd, corner_rbf, corner_rtd, corner_rtf))
        
#         edge_lb = np.setdiff1d(edge_lb, all_corners, assume_unique=True)
#         edge_lt = np.setdiff1d(edge_lt, all_corners, assume_unique=True)
#         edge_rb = np.setdiff1d(edge_rb, all_corners, assume_unique=True)
#         edge_rt = np.setdiff1d(edge_rt, all_corners, assume_unique=True)

#         edge_bd = np.setdiff1d(edge_bd, all_corners, assume_unique=True)
#         edge_bf = np.setdiff1d(edge_bf, all_corners, assume_unique=True)
#         edge_td = np.setdiff1d(edge_td, all_corners, assume_unique=True)
#         edge_tf = np.setdiff1d(edge_tf, all_corners, assume_unique=True)

#         edge_ld = np.setdiff1d(edge_ld, all_corners, assume_unique=True)
#         edge_lf = np.setdiff1d(edge_lf, all_corners, assume_unique=True)
#         edge_rd = np.setdiff1d(edge_rd, all_corners, assume_unique=True)
#         edge_rf = np.setdiff1d(edge_rf, all_corners, assume_unique=True)
        
#         all_edges = np.hstack((edge_lb, edge_lt, edge_rb, edge_rt, edge_bd, edge_bf, 
#                                edge_td, edge_tf, edge_ld, edge_lf, edge_rd, edge_rf, 
#                                all_corners))
        
#         left   = np.setdiff1d(left  , all_edges, assume_unique=True)
#         right  = np.setdiff1d(right , all_edges, assume_unique=True)
#         bottom = np.setdiff1d(bottom, all_edges, assume_unique=True)
#         top    = np.setdiff1d(top   , all_edges, assume_unique=True)
#         behind = np.setdiff1d(behind, all_edges, assume_unique=True)
#         front  = np.setdiff1d(front , all_edges, assume_unique=True)
        
#         #sort edges (required to assign the good pair of nodes)
#         edge_lb = edge_lb[np.argsort(crd[edge_lb,2])]
#         edge_lt = edge_lt[np.argsort(crd[edge_lt,2])]
#         edge_rb = edge_rb[np.argsort(crd[edge_rb,2])]
#         edge_rt = edge_rt[np.argsort(crd[edge_rt,2])]
        
#         edge_bd = edge_bd[np.argsort(crd[edge_bd,0])] 
#         edge_bf = edge_bf[np.argsort(crd[edge_bf,0])]
#         edge_td = edge_td[np.argsort(crd[edge_td,0])]
#         edge_tf = edge_tf[np.argsort(crd[edge_tf,0])]
        
#         edge_ld = edge_ld[np.argsort(crd[edge_ld,1])]
#         edge_lf = edge_lf[np.argsort(crd[edge_lf,1])]
#         edge_rd = edge_rd[np.argsort(crd[edge_rd,1])]
#         edge_rf = edge_rf[np.argsort(crd[edge_rf,1])]
        
#         #sort adjacent faces to ensure node correspondance
#         decimal_round = int(-np.log10(tol)-1)
#         left   = left  [np.lexsort((crd[left  ,1], crd[left  ,2].round(decimal_round)))]
#         right  = right [np.lexsort((crd[right ,1], crd[right ,2].round(decimal_round)))]
#         bottom = bottom[np.lexsort((crd[bottom,0], crd[bottom,2].round(decimal_round)))]
#         top    = top   [np.lexsort((crd[top   ,0], crd[top   ,2].round(decimal_round)))]
#         behind = behind[np.lexsort((crd[behind,0], crd[behind,1].round(decimal_round)))]
#         front  = front [np.lexsort((crd[front ,0], crd[front ,1].round(decimal_round)))]
                                        
#         #now apply periodic boudary conditions        
#         dx = xmax-xmin ; dy = ymax-ymin ; dz = zmax-zmin        
#         #[EpsXX, EpsYY, EpsZZ, EpsYZ, EpsXZ, EpsXY]
#         #Left/right faces
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0]], [np.full_like(right,1), np.full_like(left,-1), np.full_like(right,-dx, dtype=float)], [right,left,np.full_like(right,NodeCD[0][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0]], [np.full_like(right,1), np.full_like(left,-1), np.full_like(right,-dx, dtype=float)], [right,left,np.full_like(right,NodeCD[1][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0]], [np.full_like(right,1), np.full_like(left,-1), np.full_like(right,-dx, dtype=float)], [right,left,np.full_like(right,NodeCD[2][0])], ProblemID = ProblemID)
#         #top/bottom faces
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top,-dy, dtype=float)], [top,bottom,np.full_like(top,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top,-dy, dtype=float)], [top,bottom,np.full_like(top,NodeCD[1][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][1]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top,-dy, dtype=float)], [top,bottom,np.full_like(top,NodeCD[2][1])], ProblemID = ProblemID)
#         #front/behind faces
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][2]], [np.full_like(front,1), np.full_like(behind,-1), np.full_like(front,-dz, dtype=float)], [front,behind,np.full_like(front,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][2]], [np.full_like(front,1), np.full_like(behind,-1), np.full_like(front,-dz, dtype=float)], [front,behind,np.full_like(front,NodeCD[1][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][2]], [np.full_like(front,1), np.full_like(behind,-1), np.full_like(front,-dz, dtype=float)], [front,behind,np.full_like(front,NodeCD[2][2])], ProblemID = ProblemID)
                
#         #elimination of DOF from edge left/top -> edge left/bottom
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1]], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1), np.full_like(edge_lt,-dy, dtype=float)], [edge_lt, edge_lb, np.full_like(edge_lt,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1]], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1), np.full_like(edge_lt,-dy, dtype=float)], [edge_lt, edge_lb, np.full_like(edge_lt,NodeCD[1][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][1]], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1), np.full_like(edge_lt,-dy, dtype=float)], [edge_lt, edge_lb, np.full_like(edge_lt,NodeCD[2][1])], ProblemID = ProblemID)        
#         #elimination of DOF from edge right/bottom -> edge left/bottom
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0]], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1), np.full_like(edge_rb,-dx, dtype=float)], [edge_rb, edge_lb, np.full_like(edge_lt,NodeCD[0][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0]], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1), np.full_like(edge_rb,-dx, dtype=float)], [edge_rb, edge_lb, np.full_like(edge_lt,NodeCD[1][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0]], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1), np.full_like(edge_rb,-dx, dtype=float)], [edge_rb, edge_lb, np.full_like(edge_lt,NodeCD[2][0])], ProblemID = ProblemID)        
#         #elimination of DOF from edge right/top -> edge left/bottom
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0],VarCD[0][1]], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1), np.full_like(edge_rt,-dx, dtype=float), np.full_like(edge_rt,-dy, dtype=float)], [edge_rt, edge_lb, np.full_like(edge_rt,NodeCD[0][0]), np.full_like(edge_rt,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0],VarCD[1][1]], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1), np.full_like(edge_rt,-dx, dtype=float), np.full_like(edge_rt,-dy, dtype=float)], [edge_rt, edge_lb, np.full_like(edge_rt,NodeCD[1][0]), np.full_like(edge_rt,NodeCD[1][1])], ProblemID = ProblemID)                
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0],VarCD[2][1]], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1), np.full_like(edge_rt,-dx, dtype=float), np.full_like(edge_rt,-dy, dtype=float)], [edge_rt, edge_lb, np.full_like(edge_rt,NodeCD[2][0]), np.full_like(edge_rt,NodeCD[2][1])], ProblemID = ProblemID)                
                                       
#         #elimination of DOF from edge top/behind -> edge bottom/behind
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1]], [np.full_like(edge_td,1), np.full_like(edge_bd,-1), np.full_like(edge_td,-dy, dtype=float)], [edge_td, edge_bd, np.full_like(edge_td,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1]], [np.full_like(edge_td,1), np.full_like(edge_bd,-1), np.full_like(edge_td,-dy, dtype=float)], [edge_td, edge_bd, np.full_like(edge_td,NodeCD[1][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][1]], [np.full_like(edge_td,1), np.full_like(edge_bd,-1), np.full_like(edge_td,-dy, dtype=float)], [edge_td, edge_bd, np.full_like(edge_td,NodeCD[2][1])], ProblemID = ProblemID)        
#         #elimination of DOF from edge bottom/front -> edge bottom/behind
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][2]], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1), np.full_like(edge_bf,-dz, dtype=float)], [edge_bf, edge_bd, np.full_like(edge_bf,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][2]], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1), np.full_like(edge_bf,-dz, dtype=float)], [edge_bf, edge_bd, np.full_like(edge_bf,NodeCD[1][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][2]], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1), np.full_like(edge_bf,-dz, dtype=float)], [edge_bf, edge_bd, np.full_like(edge_bf,NodeCD[2][2])], ProblemID = ProblemID)        
#         #elimination of DOF from edge top/front -> edge bottom/behind
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1],VarCD[0][2]], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1), np.full_like(edge_tf,-dy, dtype=float), np.full_like(edge_tf,-dz, dtype=float)], [edge_tf, edge_bd, np.full_like(edge_tf,NodeCD[0][1]), np.full_like(edge_tf,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1],VarCD[1][2]], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1), np.full_like(edge_tf,-dy, dtype=float), np.full_like(edge_tf,-dz, dtype=float)], [edge_tf, edge_bd, np.full_like(edge_tf,NodeCD[1][1]), np.full_like(edge_tf,NodeCD[1][2])], ProblemID = ProblemID)                
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][1],VarCD[2][2]], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1), np.full_like(edge_tf,-dy, dtype=float), np.full_like(edge_tf,-dz, dtype=float)], [edge_tf, edge_bd, np.full_like(edge_tf,NodeCD[2][1]), np.full_like(edge_tf,NodeCD[2][2])], ProblemID = ProblemID)                
   
#         #elimination of DOF from edge right/behind -> edge left/behind
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0]], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dx, dtype=float)], [edge_rd, edge_ld, np.full_like(edge_ld,NodeCD[0][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0]], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dx, dtype=float)], [edge_rd, edge_ld, np.full_like(edge_ld,NodeCD[1][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0]], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dx, dtype=float)], [edge_rd, edge_ld, np.full_like(edge_ld,NodeCD[2][0])], ProblemID = ProblemID)        
#         #elimination of DOF from edge left/front -> edge left/behind
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][2]], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dz, dtype=float)], [edge_lf, edge_ld, np.full_like(edge_ld,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][2]], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dz, dtype=float)], [edge_lf, edge_ld, np.full_like(edge_ld,NodeCD[1][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][2]], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dz, dtype=float)], [edge_lf, edge_ld, np.full_like(edge_ld,NodeCD[2][2])], ProblemID = ProblemID)        
#         #elimination of DOF from edge right/front -> edge left/behind
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0],VarCD[0][2]], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1), np.full_like(edge_rf,-dx, dtype=float), np.full_like(edge_rf,-dz, dtype=float)], [edge_rf, edge_ld, np.full_like(edge_rf,NodeCD[0][0]), np.full_like(edge_rf,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0],VarCD[1][2]], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1), np.full_like(edge_rf,-dx, dtype=float), np.full_like(edge_rf,-dz, dtype=float)], [edge_rf, edge_ld, np.full_like(edge_rf,NodeCD[1][0]), np.full_like(edge_rf,NodeCD[1][2])], ProblemID = ProblemID)                
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0],VarCD[2][2]], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1), np.full_like(edge_rf,-dx, dtype=float), np.full_like(edge_rf,-dz, dtype=float)], [edge_rf, edge_ld, np.full_like(edge_rf,NodeCD[2][0]), np.full_like(edge_rf,NodeCD[2][2])], ProblemID = ProblemID)
        
#         # #### CORNER ####
#         #elimination of DOF from corner right/bottom/behind (corner_rbd) -> corner left/bottom/behind (corner_lbd) 
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0]], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbd,-dx, dtype=float)], [corner_rbd, corner_lbd, np.full_like(corner_rbd,NodeCD[0][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0]], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbd,-dx, dtype=float)], [corner_rbd, corner_lbd, np.full_like(corner_rbd,NodeCD[1][0])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0]], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbd,-dx, dtype=float)], [corner_rbd, corner_lbd, np.full_like(corner_rbd,NodeCD[2][0])], ProblemID = ProblemID) 
#         #elimination of DOF from corner left/top/behind (corner_ltd) -> corner left/bottom/behind (corner_lbd) 
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1]], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltd,-dy, dtype=float)], [corner_ltd, corner_lbd, np.full_like(corner_ltd,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1]], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltd,-dy, dtype=float)], [corner_ltd, corner_lbd, np.full_like(corner_ltd,NodeCD[1][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][1]], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltd,-dy, dtype=float)], [corner_ltd, corner_lbd, np.full_like(corner_ltd,NodeCD[2][1])], ProblemID = ProblemID)
#         #elimination of DOF from corner left/bottom/front (corner_lbf) -> corner left/bottom/behind (corner_lbd) 
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][2]], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_lbf,-dz, dtype=float)], [corner_lbf, corner_lbd, np.full_like(corner_lbf,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][2]], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_lbf,-dz, dtype=float)], [corner_lbf, corner_lbd, np.full_like(corner_lbf,NodeCD[1][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][2]], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_lbf,-dz, dtype=float)], [corner_lbf, corner_lbd, np.full_like(corner_lbf,NodeCD[2][2])], ProblemID = ProblemID)
#         #elimination of DOF from corner right/top/behind (corner_rtd) -> corner left/bottom/behind (corner_lbd) 
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0],VarCD[0][1]], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtd,-dx, dtype=float), np.full_like(corner_rtd,-dy, dtype=float)], [corner_rtd, corner_lbd, np.full_like(corner_rtd,NodeCD[0][0]), np.full_like(corner_rtd,NodeCD[0][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0],VarCD[1][1]], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtd,-dx, dtype=float), np.full_like(corner_rtd,-dy, dtype=float)], [corner_rtd, corner_lbd, np.full_like(corner_rtd,NodeCD[1][0]), np.full_like(corner_rtd,NodeCD[1][1])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0],VarCD[2][1]], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtd,-dx, dtype=float), np.full_like(corner_rtd,-dy, dtype=float)], [corner_rtd, corner_lbd, np.full_like(corner_rtd,NodeCD[2][0]), np.full_like(corner_rtd,NodeCD[2][1])], ProblemID = ProblemID)
#         #elimination of DOF from corner left/top/front (corner_ltf) -> corner left/bottom/behind (corner_lbd) 
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][1],VarCD[0][2]], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltf,-dy, dtype=float), np.full_like(corner_ltf,-dz, dtype=float)], [corner_ltf, corner_lbd, np.full_like(corner_ltf,NodeCD[0][1]), np.full_like(corner_ltf,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][1],VarCD[1][2]], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltf,-dy, dtype=float), np.full_like(corner_ltf,-dz, dtype=float)], [corner_ltf, corner_lbd, np.full_like(corner_ltf,NodeCD[1][1]), np.full_like(corner_ltf,NodeCD[1][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][1],VarCD[2][2]], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltf,-dy, dtype=float), np.full_like(corner_ltf,-dz, dtype=float)], [corner_ltf, corner_lbd, np.full_like(corner_ltf,NodeCD[2][1]), np.full_like(corner_ltf,NodeCD[2][2])], ProblemID = ProblemID)
#         #elimination of DOF from corner right/bottom/front (corner_rbf) -> corner left/bottom/behind (corner_lbd) 
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0],VarCD[0][2]], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbf,-dx, dtype=float), np.full_like(corner_rbf,-dz, dtype=float)], [corner_rbf, corner_lbd, np.full_like(corner_rbf,NodeCD[0][0]), np.full_like(corner_rbf,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0],VarCD[1][2]], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbf,-dx, dtype=float), np.full_like(corner_rbf,-dz, dtype=float)], [corner_rbf, corner_lbd, np.full_like(corner_rbf,NodeCD[1][0]), np.full_like(corner_rbf,NodeCD[1][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0],VarCD[2][2]], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbf,-dx, dtype=float), np.full_like(corner_rbf,-dz, dtype=float)], [corner_rbf, corner_lbd, np.full_like(corner_rbf,NodeCD[2][0]), np.full_like(corner_rbf,NodeCD[2][2])], ProblemID = ProblemID)
        
        
                
#         #elimination of DOF from corner right/top/front (corner_rtf) -> corner left/bottom/behind (corner_lbd) 
#         BoundaryCondition('MPC', ['DispX','DispX',VarCD[0][0],VarCD[0][1], VarCD[0][2]], 
#                                   [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtf,-dx, dtype=float), np.full_like(corner_rtf,-dy, dtype=float), np.full_like(corner_rtf,-dz, dtype=float)], 
#                                   [corner_rtf, corner_lbd, np.full_like(corner_rtf,NodeCD[0][0]), np.full_like(corner_rtf,NodeCD[0][1]), np.full_like(corner_rtf,NodeCD[0][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispY','DispY',VarCD[1][0],VarCD[1][1], VarCD[1][2]], 
#                                   [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtf,-dx, dtype=float), np.full_like(corner_rtf,-dy, dtype=float), np.full_like(corner_rtf,-0.5*dz, dtype=float)], 
#                                   [corner_rtf, corner_lbd, np.full_like(corner_rtf,NodeCD[1][0]), np.full_like(corner_rtf,NodeCD[1][1]), np.full_like(corner_rtf,NodeCD[1][2])], ProblemID = ProblemID)
#         BoundaryCondition('MPC', ['DispZ','DispZ',VarCD[2][0],VarCD[2][1], VarCD[2][2]], 
#                                   [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtf,-dx, dtype=float), np.full_like(corner_rtf,-dy, dtype=float), np.full_like(corner_rtf,-dz, dtype=float)    ], 
#                                   [corner_rtf, corner_lbd, np.full_like(corner_rtf,NodeCD[2][0]), np.full_like(corner_rtf,NodeCD[2][1]), np.full_like(corner_rtf,NodeCD[2][2])], ProblemID = ProblemID)

#         #if rot DOF are used, apply continuity of the rotational dof
#         list_rot_var = []
#         if 'RotX' in ModelingSpace.ListVariable(): list_rot_var.append('RotX')
#         if 'RotY' in ModelingSpace.ListVariable(): list_rot_var.append('RotY')
#         if 'RotZ' in ModelingSpace.ListVariable(): list_rot_var.append('RotZ')
        
#         for var in list_rot_var: 
#             #### FACES ####
#             BoundaryCondition('MPC', [var,var], [np.full_like(right,1), np.full_like(left,-1)], [right,left], ProblemID = ProblemID)
#             BoundaryCondition('MPC', [var,var], [np.full_like(top,1), np.full_like(bottom,-1)], [top,bottom], ProblemID = ProblemID)
#             BoundaryCondition('MPC', [var,var], [np.full_like(front,1), np.full_like(behind,-1)], [front,behind], ProblemID = ProblemID)
                     
#             #### EDGES ####
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1)], [edge_lt, edge_lb], ProblemID = ProblemID)        
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1)], [edge_rb, edge_lb], ProblemID = ProblemID)        
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1)], [edge_rt, edge_lb], ProblemID = ProblemID)        
            
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_td,1), np.full_like(edge_bd,-1)], [edge_td, edge_bd], ProblemID = ProblemID)        
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1)], [edge_bf, edge_bd], ProblemID = ProblemID)        
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1)], [edge_tf, edge_bd], ProblemID = ProblemID)        

#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1)], [edge_rd, edge_ld], ProblemID = ProblemID)        
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1)], [edge_lf, edge_ld], ProblemID = ProblemID)        
#             BoundaryCondition('MPC', [var,var], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1)], [edge_rf, edge_ld], ProblemID = ProblemID)        
                           
#             #### CORNERS ####
#             BoundaryCondition('MPC', [var,var], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1)], [corner_rbd, corner_lbd], ProblemID = ProblemID)                       
#             BoundaryCondition('MPC', [var,var], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1)], [corner_ltd, corner_lbd], ProblemID = ProblemID)                        
#             BoundaryCondition('MPC', [var,var], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1)], [corner_lbf, corner_lbd], ProblemID = ProblemID)            
#             BoundaryCondition('MPC', [var,var], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1)], [corner_rtd, corner_lbd], ProblemID = ProblemID)
#             BoundaryCondition('MPC', [var,var], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1)], [corner_ltf, corner_lbd], ProblemID = ProblemID)            
#             BoundaryCondition('MPC', [var,var], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1)], [corner_rbf, corner_lbd], ProblemID = ProblemID)
#             BoundaryCondition('MPC', [var,var], [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1)], [corner_rtf, corner_lbd], ProblemID = ProblemID)


def DefinePeriodicBoundaryCondition(mesh, NodeEps, VarEps, dim='3D', tol=1e-8, ProblemID = 'MainProblem'):
    """
    Parameters
    ----------
    mesh : mesh ID or mesh object
        A periodic mesh to apply the periodic boundary conditions
    NodeEps : lise of int
        NodeEps is a list containing the node index of strain tensor component (virtual node)
        In 2D: [EpsXX, EpsYY, EpsXY]
        In 3D: [EpsXX, EpsYY, EpsZZ, EpsXY, EpsXZ, EpsYZ]
    VarEps : list of string
        VarEps is a list containing the variable id used for each component
    dim : '2D' or '3D', optional
        This parameter is used to define if the periodicity is in 2D or in 3D.
        A periodicity in 2D can be associated with a 3D mesh. 
        The default is '2D'.
    tol : float, optional
        Tolerance for the position of nodes. The default is 1e-8.
    ProblemID : ProblemID on which the boundary conditions are applied
        The default is 'MainProblem'.

    Returns
    -------
    None.

    """
    #TODO: add set to the mesh and don't compute the set if the set are already present
    if dim in ['2D','2d']: dim = 2
    if dim in ['3D','3d']: dim = 3

    if isinstance(mesh, str): mesh = MeshBase.GetAll()[mesh]
    
    numGeometricMesh = mesh.FindCoordinateID('X')
    assert(numGeometricMesh == mesh.FindCoordinateID('X'), "Not possible to define periodic condition on the given sepearated mesh" )
    if dim == 3: assert(numGeometricMesh == mesh.FindCoordinateID('Z'), "Not possible to define periodic condition on the given sepearated mesh" )
     
    GeometricMesh = mesh.GetListMesh()[numGeometricMesh]
    crd = GeometricMesh.GetNodeCoordinates()
    xmax = np.max(crd[:,0]) ; xmin = np.min(crd[:,0])
    ymax = np.max(crd[:,1]) ; ymin = np.min(crd[:,1])
    
    if dim == 3:                        
        zmax = np.max(crd[:,2]) ; zmin = np.min(crd[:,2])
  
    if dim == 2:                       
        #Define node sets
        left   = np.where( (np.abs(crd[:,0] - xmin) < tol) * (np.abs(crd[:,1] - ymin) > tol) * (np.abs(crd[:,1] - ymax) > tol))[0]
        right  = np.where( (np.abs(crd[:,0] - xmax) < tol) * (np.abs(crd[:,1] - ymin) > tol) * (np.abs(crd[:,1] - ymax) > tol))[0]
        bottom = np.where( (np.abs(crd[:,1] - ymin) < tol) * (np.abs(crd[:,0] - xmin) > tol) * (np.abs(crd[:,0] - xmax) > tol))[0]
        top    = np.where( (np.abs(crd[:,1] - ymax) < tol) * (np.abs(crd[:,0] - xmin) > tol) * (np.abs(crd[:,0] - xmax) > tol))[0]        
    
        corner_lb = np.where((np.abs(crd[:,0] - xmin) < tol) * (np.abs(crd[:,1] - ymin) < tol))[0] #corner left bottom
        corner_rb = np.where((np.abs(crd[:,0] - xmax) < tol) * (np.abs(crd[:,1] - ymin) < tol))[0] #corner right bottom
        corner_lt = np.where((np.abs(crd[:,0] - xmin) < tol) * (np.abs(crd[:,1] - ymax) < tol))[0] #corner left top
        corner_rt = np.where((np.abs(crd[:,0] - xmax) < tol) * (np.abs(crd[:,1] - ymax) < tol))[0] #corner right top

        left = left[np.argsort(crd[left,1])]
        right = right[np.argsort(crd[right,1])]
        top = top[np.argsort(crd[top,0])]
        bottom = bottom[np.argsort(crd[bottom,0])]
        
        ################ Define set of nodes for PGD mesh #####################
        mesh.AddSetOfNodes([left],      [numGeometricMesh], ID='left')
        mesh.AddSetOfNodes([right],     [numGeometricMesh], ID='right')
        mesh.AddSetOfNodes([top],       [numGeometricMesh], ID='top')
        mesh.AddSetOfNodes([bottom],    [numGeometricMesh], ID='bottom')
        mesh.AddSetOfNodes([corner_lb], [numGeometricMesh], ID='corner_lb')
        mesh.AddSetOfNodes([corner_rb], [numGeometricMesh], ID='corner_rb')
        mesh.AddSetOfNodes([corner_lt], [numGeometricMesh], ID='corner_lt')
        mesh.AddSetOfNodes([corner_rt], [numGeometricMesh], ID='corner_rt')
        
        mesh.AddSetOfNodes([np.full_like(right, NodeEps[0])], [numGeometricMesh], ID='EpsXX_right')
        mesh.AddSetOfNodes([np.full_like(right, NodeEps[2])], [numGeometricMesh], ID='EpsXY_right')
        mesh.AddSetOfNodes([np.full_like(top,NodeEps[2])],    [numGeometricMesh], ID='EpsXY_top')
        mesh.AddSetOfNodes([np.full_like(top,NodeEps[1])],    [numGeometricMesh], ID='EpsYY_top')        
        mesh.AddSetOfNodes([np.full_like(corner_lt,NodeEps[0])], [numGeometricMesh], ID='EpsXX_corner')
        mesh.AddSetOfNodes([np.full_like(corner_lt,NodeEps[1])], [numGeometricMesh], ID='EpsYY_corner')
        mesh.AddSetOfNodes([np.full_like(corner_lt,NodeEps[2])], [numGeometricMesh], ID='EpsXY_corner')
        
        ############## Apply Boundary conditions ##############################
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0]], [np.full_like(right, 1), np.full_like(left, -1), np.full_like(right, -(xmax-xmin), dtype=float)],  ['right','left','EpsXX_right'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[2]], [np.full_like(right,1), np.full_like(left,-1), np.full_like(right,-0.5*(xmax-xmin), dtype=float)], ['right','left','EpsXY_right'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[2]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top,-0.5*(ymax-ymin), dtype=float)], ['top','bottom',np.full_like(top,NodeEps[2])], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top,-(ymax-ymin), dtype=float)], ['top','bottom',np.full_like(top,NodeEps[1])], ProblemID = ProblemID)
        
        #elimination of DOF from edge left/top -> edge left/bottom
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1]], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1), np.full_like(corner_lt,-(ymax-ymin), dtype=float)], ['corner_lt', 'corner_lb', 'EpsYY_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[2]], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1), np.full_like(corner_lt,-0.5*(ymax-ymin), dtype=float)], ['corner_lt', 'corner_lb', 'EpsXY_corner'], ProblemID = ProblemID)
        #elimination of DOF from edge right/bottom -> edge left/bottom
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0]], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1), np.full_like(corner_rb,-(xmax-xmin), dtype=float)], ['corner_rb', 'corner_lb', 'EpsXX_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[2]], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1), np.full_like(corner_rb,-0.5*(xmax-xmin), dtype=float)], ['corner_rb', 'corner_lb', np.full_like(corner_lt, NodeEps[2])], ProblemID = ProblemID)
        #elimination of DOF from edge right/top -> edge left/bottom
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0],VarEps[2]], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1), np.full_like(corner_rt,-(xmax-xmin), dtype=float), np.full_like(corner_rt,-0.5*(ymax-ymin), dtype=float)], ['corner_rt', 'corner_lb', 'EpsXX_corner', 'EpsXY_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[2],VarEps[1]], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1), np.full_like(corner_rt,-0.5*(xmax-xmin), dtype=float), np.full_like(corner_rt,-(ymax-ymin), dtype=float)], ['corner_rt', 'corner_lb', 'EpsXY_corner', 'EpsYY_corner'], ProblemID = ProblemID)                
                                       
                      
        #if rot DOF are used, apply continuity of the rotational dof
        if 'RotZ' in ModelingSpace.ListVariable():
            BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(right,1), np.full_like(left,-1)], [right,left], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(top,1), np.full_like(bottom,-1)], [top,bottom], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1)], [corner_lt, corner_lb], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1)], [corner_rb, corner_lb], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotZ','RotZ'], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1)], [corner_rt, corner_lb], ProblemID = ProblemID)
        if 'RotY' in ModelingSpace.ListVariable():
            BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(right,1), np.full_like(left,-1)], [right,left], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(top,1), np.full_like(bottom,-1)], [top,bottom], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1)], [corner_lt, corner_lb], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1)], [corner_rb, corner_lb], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotY','RotY'], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1)], [corner_rt, corner_lb], ProblemID = ProblemID)
        if 'RotX' in ModelingSpace.ListVariable():
            BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(right,1), np.full_like(left,-1)], [right,left], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(top,1), np.full_like(bottom,-1)], [top,bottom], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(corner_lt,1), np.full_like(corner_lb,-1)], [corner_lt, corner_lb], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(corner_rb,1), np.full_like(corner_lb,-1)], [corner_rb, corner_lb], ProblemID = ProblemID)
            BoundaryCondition('MPC', ['RotX','RotX'], [np.full_like(corner_rt,1), np.full_like(corner_lb,-1)], [corner_rt, corner_lb], ProblemID = ProblemID)
        
        
        #StrainNode[0] - 'DispX' is a virtual dof for EXX
        #StrainNode[0] - 'DispY' is a virtual dof for EXY
        #StrainNode[1] - 'DispX' is a non used node -> need to be blocked
        #StrainNode[1] - 'DispY' is a virtual dof for EYY
        
    elif dim == 3:                        
        
        #Define node sets
        left   = np.where( np.abs(crd[:,0] - xmin) < tol )[0]
        right  = np.where( np.abs(crd[:,0] - xmax) < tol )[0]
        bottom = np.where( np.abs(crd[:,1] - ymin) < tol )[0]
        top    = np.where( np.abs(crd[:,1] - ymax) < tol )[0]
        behind = np.where( np.abs(crd[:,2] - zmin) < tol )[0]
        front  = np.where( np.abs(crd[:,2] - zmax) < tol )[0]
        
        #extract edge from the intersection of faces
        #l = left, r = right, b = bottom, t = top, f = front, d = behind
        edge_lb = np.intersect1d(left , bottom, assume_unique=True)
        edge_lt = np.intersect1d(left , top   , assume_unique=True)
        edge_rb = np.intersect1d(right, bottom, assume_unique=True)
        edge_rt = np.intersect1d(right, top   , assume_unique=True)
        
        edge_bd = np.intersect1d(bottom, behind, assume_unique=True)
        edge_bf = np.intersect1d(bottom, front , assume_unique=True)
        edge_td = np.intersect1d(top   , behind, assume_unique=True)
        edge_tf = np.intersect1d(top   , front , assume_unique=True)
        
        edge_ld = np.intersect1d(left , behind, assume_unique=True)
        edge_lf = np.intersect1d(left , front , assume_unique=True)
        edge_rd = np.intersect1d(right, behind, assume_unique=True)
        edge_rf = np.intersect1d(right, front , assume_unique=True)        
        
        #extract corners from the intersection of edges
        corner_lbd = np.intersect1d(edge_lb , edge_bd, assume_unique=True) 
        corner_lbf = np.intersect1d(edge_lb , edge_bf, assume_unique=True)
        corner_ltd = np.intersect1d(edge_lt , edge_td, assume_unique=True)
        corner_ltf = np.intersect1d(edge_lt , edge_tf, assume_unique=True)
        corner_rbd = np.intersect1d(edge_rb , edge_bd, assume_unique=True)
        corner_rbf = np.intersect1d(edge_rb , edge_bf, assume_unique=True)
        corner_rtd = np.intersect1d(edge_rt , edge_td, assume_unique=True)
        corner_rtf = np.intersect1d(edge_rt , edge_tf, assume_unique=True)
        
        all_corners = np.hstack((corner_lbd, corner_lbf, corner_ltd, corner_ltf, 
                                 corner_rbd, corner_rbf, corner_rtd, corner_rtf))
        
        edge_lb = np.setdiff1d(edge_lb, all_corners, assume_unique=True)
        edge_lt = np.setdiff1d(edge_lt, all_corners, assume_unique=True)
        edge_rb = np.setdiff1d(edge_rb, all_corners, assume_unique=True)
        edge_rt = np.setdiff1d(edge_rt, all_corners, assume_unique=True)

        edge_bd = np.setdiff1d(edge_bd, all_corners, assume_unique=True)
        edge_bf = np.setdiff1d(edge_bf, all_corners, assume_unique=True)
        edge_td = np.setdiff1d(edge_td, all_corners, assume_unique=True)
        edge_tf = np.setdiff1d(edge_tf, all_corners, assume_unique=True)

        edge_ld = np.setdiff1d(edge_ld, all_corners, assume_unique=True)
        edge_lf = np.setdiff1d(edge_lf, all_corners, assume_unique=True)
        edge_rd = np.setdiff1d(edge_rd, all_corners, assume_unique=True)
        edge_rf = np.setdiff1d(edge_rf, all_corners, assume_unique=True)
        
        all_edges = np.hstack((edge_lb, edge_lt, edge_rb, edge_rt, edge_bd, edge_bf, 
                               edge_td, edge_tf, edge_ld, edge_lf, edge_rd, edge_rf, 
                               all_corners))
        
        left   = np.setdiff1d(left  , all_edges, assume_unique=True)
        right  = np.setdiff1d(right , all_edges, assume_unique=True)
        bottom = np.setdiff1d(bottom, all_edges, assume_unique=True)
        top    = np.setdiff1d(top   , all_edges, assume_unique=True)
        behind = np.setdiff1d(behind, all_edges, assume_unique=True)
        front  = np.setdiff1d(front , all_edges, assume_unique=True)
        
        #sort edges (required to assign the good pair of nodes)
        edge_lb = edge_lb[np.argsort(crd[edge_lb,2])]
        edge_lt = edge_lt[np.argsort(crd[edge_lt,2])]
        edge_rb = edge_rb[np.argsort(crd[edge_rb,2])]
        edge_rt = edge_rt[np.argsort(crd[edge_rt,2])]
        
        edge_bd = edge_bd[np.argsort(crd[edge_bd,0])] 
        edge_bf = edge_bf[np.argsort(crd[edge_bf,0])]
        edge_td = edge_td[np.argsort(crd[edge_td,0])]
        edge_tf = edge_tf[np.argsort(crd[edge_tf,0])]
        
        edge_ld = edge_ld[np.argsort(crd[edge_ld,1])]
        edge_lf = edge_lf[np.argsort(crd[edge_lf,1])]
        edge_rd = edge_rd[np.argsort(crd[edge_rd,1])]
        edge_rf = edge_rf[np.argsort(crd[edge_rf,1])]
        
        #sort adjacent faces to ensure node correspondance
        decimal_round = int(-np.log10(tol)-1)
        left   = left  [np.lexsort((crd[left  ,1], crd[left  ,2].round(decimal_round)))]
        right  = right [np.lexsort((crd[right ,1], crd[right ,2].round(decimal_round)))]
        bottom = bottom[np.lexsort((crd[bottom,0], crd[bottom,2].round(decimal_round)))]
        top    = top   [np.lexsort((crd[top   ,0], crd[top   ,2].round(decimal_round)))]
        behind = behind[np.lexsort((crd[behind,0], crd[behind,1].round(decimal_round)))]
        front  = front [np.lexsort((crd[front ,0], crd[front ,1].round(decimal_round)))]
        
        
        
        ################ Define set of nodes for PGD mesh #####################
        mesh.AddSetOfNodes([left],      [numGeometricMesh], ID='left')
        mesh.AddSetOfNodes([right],     [numGeometricMesh], ID='right')
        mesh.AddSetOfNodes([bottom],    [numGeometricMesh], ID='bottom')
        mesh.AddSetOfNodes([top],       [numGeometricMesh], ID='top')
        mesh.AddSetOfNodes([behind],    [numGeometricMesh], ID='behind')
        mesh.AddSetOfNodes([front],     [numGeometricMesh], ID='front')
        
        mesh.AddSetOfNodes([edge_lb], [numGeometricMesh], ID='edge_lb')
        mesh.AddSetOfNodes([edge_lt], [numGeometricMesh], ID='edge_lt')
        mesh.AddSetOfNodes([edge_rb], [numGeometricMesh], ID='edge_rb')
        mesh.AddSetOfNodes([edge_rt], [numGeometricMesh], ID='edge_rt')

        mesh.AddSetOfNodes([edge_bd], [numGeometricMesh], ID='edge_bd')
        mesh.AddSetOfNodes([edge_bf], [numGeometricMesh], ID='edge_bf')
        mesh.AddSetOfNodes([edge_td], [numGeometricMesh], ID='edge_td')
        mesh.AddSetOfNodes([edge_tf], [numGeometricMesh], ID='edge_tf')

        mesh.AddSetOfNodes([edge_ld], [numGeometricMesh], ID='edge_ld')
        mesh.AddSetOfNodes([edge_lf], [numGeometricMesh], ID='edge_lf')
        mesh.AddSetOfNodes([edge_rd], [numGeometricMesh], ID='edge_rd')
        mesh.AddSetOfNodes([edge_rf], [numGeometricMesh], ID='edge_rf')
           
        mesh.AddSetOfNodes([corner_lbd], [numGeometricMesh], ID='corner_lbd')
        mesh.AddSetOfNodes([corner_lbf], [numGeometricMesh], ID='corner_lbf')
        mesh.AddSetOfNodes([corner_ltd], [numGeometricMesh], ID='corner_ltd')
        mesh.AddSetOfNodes([corner_ltf], [numGeometricMesh], ID='corner_ltf')
        mesh.AddSetOfNodes([corner_rbd], [numGeometricMesh], ID='corner_rbd')
        mesh.AddSetOfNodes([corner_rbf], [numGeometricMesh], ID='corner_rbf')
        mesh.AddSetOfNodes([corner_rtd], [numGeometricMesh], ID='corner_rtd')
        mesh.AddSetOfNodes([corner_rtf], [numGeometricMesh], ID='corner_rtf')
                
        mesh.AddSetOfNodes([np.full_like(right, NodeEps[0])], [numGeometricMesh], ID='EpsXX_right')
        mesh.AddSetOfNodes([np.full_like(right, NodeEps[3])], [numGeometricMesh], ID='EpsXY_right')
        mesh.AddSetOfNodes([np.full_like(right, NodeEps[4])], [numGeometricMesh], ID='EpsXZ_right')
        mesh.AddSetOfNodes([np.full_like(top,NodeEps[3])],    [numGeometricMesh], ID='EpsXY_top')
        mesh.AddSetOfNodes([np.full_like(top,NodeEps[1])],    [numGeometricMesh], ID='EpsYY_top')
        mesh.AddSetOfNodes([np.full_like(top,NodeEps[5])],    [numGeometricMesh], ID='EpsYZ_top')
        mesh.AddSetOfNodes([np.full_like(front,NodeEps[4])],  [numGeometricMesh], ID='EpsXZ_front')
        mesh.AddSetOfNodes([np.full_like(front,NodeEps[5])],  [numGeometricMesh], ID='EpsYZ_front')
        mesh.AddSetOfNodes([np.full_like(front,NodeEps[2])],  [numGeometricMesh], ID='EpsZZ_front')

        mesh.AddSetOfNodes([np.full_like(edge_lt,NodeEps[0])],[numGeometricMesh], ID='EpsXX_edge_lt')
        mesh.AddSetOfNodes([np.full_like(edge_lt,NodeEps[1])],[numGeometricMesh], ID='EpsYY_edge_lt')
        mesh.AddSetOfNodes([np.full_like(edge_lt,NodeEps[3])],[numGeometricMesh], ID='EpsXY_edge_lt')
        mesh.AddSetOfNodes([np.full_like(edge_lt,NodeEps[4])],[numGeometricMesh], ID='EpsXZ_edge_lt')
        mesh.AddSetOfNodes([np.full_like(edge_lt,NodeEps[5])],[numGeometricMesh], ID='EpsYZ_edge_lt')
    
        mesh.AddSetOfNodes([np.full_like(edge_bf,NodeEps[1])],[numGeometricMesh], ID='EpsYY_edge_bf')
        mesh.AddSetOfNodes([np.full_like(edge_bf,NodeEps[2])],[numGeometricMesh], ID='EpsZZ_edge_bf')
        mesh.AddSetOfNodes([np.full_like(edge_bf,NodeEps[3])],[numGeometricMesh], ID='EpsXY_edge_bf')
        mesh.AddSetOfNodes([np.full_like(edge_bf,NodeEps[4])],[numGeometricMesh], ID='EpsXZ_edge_bf')
        mesh.AddSetOfNodes([np.full_like(edge_bf,NodeEps[5])],[numGeometricMesh], ID='EpsYZ_edge_bf')

        mesh.AddSetOfNodes([np.full_like(edge_ld,NodeEps[0])],[numGeometricMesh], ID='EpsXX_edge_ld')
        mesh.AddSetOfNodes([np.full_like(edge_ld,NodeEps[2])],[numGeometricMesh], ID='EpsZZ_edge_ld')
        mesh.AddSetOfNodes([np.full_like(edge_ld,NodeEps[3])],[numGeometricMesh], ID='EpsXY_edge_ld')
        mesh.AddSetOfNodes([np.full_like(edge_ld,NodeEps[4])],[numGeometricMesh], ID='EpsXZ_edge_ld')
        mesh.AddSetOfNodes([np.full_like(edge_ld,NodeEps[5])],[numGeometricMesh], ID='EpsYZ_edge_ld')

        mesh.AddSetOfNodes([np.full_like(corner_rbd,NodeEps[0])], [numGeometricMesh], ID='EpsXX_corner')
        mesh.AddSetOfNodes([np.full_like(corner_rbd,NodeEps[1])], [numGeometricMesh], ID='EpsYY_corner')
        mesh.AddSetOfNodes([np.full_like(corner_rbd,NodeEps[2])], [numGeometricMesh], ID='EpsZZ_corner')
        mesh.AddSetOfNodes([np.full_like(corner_rbd,NodeEps[3])], [numGeometricMesh], ID='EpsXY_corner')
        mesh.AddSetOfNodes([np.full_like(corner_rbd,NodeEps[4])], [numGeometricMesh], ID='EpsXZ_corner')
        mesh.AddSetOfNodes([np.full_like(corner_rbd,NodeEps[5])], [numGeometricMesh], ID='EpsYZ_corner')
        
        
        ############## Apply Boundary conditions ##############################
        
        dx = xmax-xmin ; dy = ymax-ymin ; dz = zmax-zmin        
        #[EpsXX, EpsYY, EpsZZ, EpsYZ, EpsXZ, EpsXY]
        #Left/right faces
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0]], [np.full_like(right,1), np.full_like(left, -1), np.full_like(right, -dx, dtype=float)]  , ['right','left','EpsXX_right'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3]], [np.full_like(right,1), np.full_like(left,-1), np.full_like(right,-0.5*dx, dtype=float)], ['right','left','EpsXY_right'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4]], [np.full_like(right,1), np.full_like(left,-1), np.full_like(right,-0.5*dx, dtype=float)], ['right','left','EpsXY_right'], ProblemID = ProblemID)
        #top/bottom faces
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[3]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top,-0.5*dy, dtype=float)], ['top','bottom','EpsXY_top'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top, -dy, dtype=float)]   , ['top','bottom','EpsYY_top'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[5]], [np.full_like(top,1), np.full_like(bottom,-1), np.full_like(top,-0.5*dy, dtype=float)], ['top','bottom','EpsYZ_top'], ProblemID = ProblemID)
        #front/behind faces
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[4]], [np.full_like(front,1), np.full_like(behind,-1), np.full_like(front,-0.5*dz, dtype=float)], ['front','behind','EpsXZ_front'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[5]], [np.full_like(front,1), np.full_like(behind,-1), np.full_like(front,-0.5*dz, dtype=float)], ['front','behind','EpsYZ_front'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[2]], [np.full_like(front,1), np.full_like(behind,-1), np.full_like(front,-dz, dtype=float)    ], ['front','behind','EpsZZ_front'], ProblemID = ProblemID)
                
        #elimination of DOF from edge left/top -> edge left/bottom
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[3]], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1), np.full_like(edge_lt,-0.5*dy, dtype=float)], ['edge_lt', 'edge_lb', 'EpsXY_edge_lt'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1]], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1), np.full_like(edge_lt,-dy, dtype=float)    ], ['edge_lt', 'edge_lb', 'EpsYY_edge_lt'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[5]], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1), np.full_like(edge_lt,-0.5*dy, dtype=float)], ['edge_lt', 'edge_lb', 'EpsYZ_edge_lt'], ProblemID = ProblemID)        
        #elimination of DOF from edge right/bottom -> edge left/bottom
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0]], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1), np.full_like(edge_rb,-dx, dtype=float)    ], ['edge_rb', 'edge_lb', 'EpsXX_edge_lt'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3]], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1), np.full_like(edge_rb,-0.5*dx, dtype=float)], ['edge_rb', 'edge_lb', 'EpsXY_edge_lt'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4]], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1), np.full_like(edge_rb,-0.5*dx, dtype=float)], ['edge_rb', 'edge_lb', 'EpsXZ_edge_lt'], ProblemID = ProblemID)        
        #elimination of DOF from edge right/top -> edge left/bottom
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0],VarEps[3]], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1), np.full_like(edge_rt,-dx, dtype=float), np.full_like(edge_rt,-0.5*dy, dtype=float)], ['edge_rt', 'edge_lb', 'EpsXX_edge_lt', 'EpsXY_edge_lt'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3],VarEps[1]], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1), np.full_like(edge_rt,-0.5*dx, dtype=float), np.full_like(edge_rt,-dy, dtype=float)], ['edge_rt', 'edge_lb', 'EpsXY_edge_lt', 'EpsYY_edge_lt'], ProblemID = ProblemID)                
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4],VarEps[5]], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1), np.full_like(edge_rt,-0.5*dx, dtype=float), np.full_like(edge_rt,-0.5*dy, dtype=float)], ['edge_rt', 'edge_lb', 'EpsXZ_edge_lt', 'EpsYZ_edge_lt'], ProblemID = ProblemID)                
                                       
        #elimination of DOF from edge top/behind -> edge bottom/behind
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[3]], [np.full_like(edge_td,1), np.full_like(edge_bd,-1), np.full_like(edge_td,-0.5*dy, dtype=float)], ['edge_td', 'edge_bd', 'EpsXY_edge_bf'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1]], [np.full_like(edge_td,1), np.full_like(edge_bd,-1), np.full_like(edge_td,-dy, dtype=float)    ], ['edge_td', 'edge_bd', 'EpsYY_edge_bf'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[5]], [np.full_like(edge_td,1), np.full_like(edge_bd,-1), np.full_like(edge_td,-0.5*dy, dtype=float)], ['edge_td', 'edge_bd', 'EpsYZ_edge_bf'], ProblemID = ProblemID)        
        #elimination of DOF from edge bottom/front -> edge bottom/behind
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[4]], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1), np.full_like(edge_bf,-0.5*dz, dtype=float)], ['edge_bf', 'edge_bd', 'EpsXZ_edge_bf'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[5]], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1), np.full_like(edge_bf,-0.5*dz, dtype=float)], ['edge_bf', 'edge_bd', 'EpsYZ_edge_bf'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[2]], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1), np.full_like(edge_bf,-dz, dtype=float)    ], ['edge_bf', 'edge_bd', 'EpsZZ_edge_bf'], ProblemID = ProblemID)        
        #elimination of DOF from edge top/front -> edge bottom/behind
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[3],VarEps[4]], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1), np.full_like(edge_tf,-0.5*dy, dtype=float), np.full_like(edge_tf,-0.5*dz, dtype=float)], ['edge_tf', 'edge_bd', 'EpsXY_edge_bf', 'EpsXZ_edge_bf'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1],VarEps[5]], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1), np.full_like(edge_tf,-dy, dtype=float)    , np.full_like(edge_tf,-0.5*dz, dtype=float)], ['edge_tf', 'edge_bd', 'EpsYY_edge_bf', 'EpsYZ_edge_bf'], ProblemID = ProblemID)                
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[5],VarEps[2]], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1), np.full_like(edge_tf,-0.5*dy, dtype=float), np.full_like(edge_tf,-dz, dtype=float)    ], ['edge_tf', 'edge_bd', 'EpsYZ_edge_bf', 'EpsZZ_edge_bf'], ProblemID = ProblemID)                
   
        #elimination of DOF from edge right/behind -> edge left/behind
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0]], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dx, dtype=float)    ], ['edge_rd', 'edge_ld', 'EpsXX_edge_ld'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3]], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-0.5*dx, dtype=float)], ['edge_rd', 'edge_ld', 'EpsXY_edge_ld'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4]], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-0.5*dx, dtype=float)], ['edge_rd', 'edge_ld', 'EpsXZ_edge_ld'], ProblemID = ProblemID)        
        #elimination of DOF from edge left/front -> edge left/behind
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[4]], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-0.5*dz, dtype=float)], ['edge_lf', 'edge_ld', 'EpsXZ_edge_ld'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[5]], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-0.5*dz, dtype=float)], ['edge_lf', 'edge_ld', 'EpsYZ_edge_ld'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[2]], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1), np.full_like(edge_rd,-dz, dtype=float)    ], ['edge_lf', 'edge_ld', 'EpsZZ_edge_ld'], ProblemID = ProblemID)        
        #elimination of DOF from edge right/front -> edge left/behind
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0],VarEps[4]], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1), np.full_like(edge_rf,-dx    , dtype=float), np.full_like(edge_rf,-0.5*dz, dtype=float)], ['edge_rf', 'edge_ld', 'EpsXX_edge_ld', 'EpsXZ_edge_ld'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3],VarEps[5]], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1), np.full_like(edge_rf,-0.5*dx, dtype=float), np.full_like(edge_rf,-0.5*dz, dtype=float)], ['edge_rf', 'edge_ld', 'EpsXY_edge_ld', 'EpsYZ_edge_ld'], ProblemID = ProblemID)                
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4],VarEps[2]], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1), np.full_like(edge_rf,-0.5*dx, dtype=float), np.full_like(edge_rf,-dz, dtype=float)    ], ['edge_rf', 'edge_ld', 'EpsXZ_edge_ld', 'EpsZZ_edge_ld'], ProblemID = ProblemID)                
        
        #### CORNER ####
        #elimination of DOF from corner right/bottom/behind (corner_rbd) -> corner left/bottom/behind (corner_lbd) 
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0]], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbd,-dx, dtype=float)    ], ['corner_rbd', 'corner_lbd', 'EpsXX_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3]], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbd,-0.5*dx, dtype=float)], ['corner_rbd', 'corner_lbd', 'EpsXY_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4]], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbd,-0.5*dx, dtype=float)], ['corner_rbd', 'corner_lbd', 'EpsXZ_corner'], ProblemID = ProblemID) 
        #elimination of DOF from corner left/top/behind (corner_ltd) -> corner left/bottom/behind (corner_lbd) 
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[3]], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltd,-0.5*dy, dtype=float)], ['corner_ltd', 'corner_lbd', 'EpsXY_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1]], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltd,-dy, dtype=float)    ], ['corner_ltd', 'corner_lbd', 'EpsYY_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[5]], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltd,-0.5*dy, dtype=float)], ['corner_ltd', 'corner_lbd', 'EpsYZ_corner'], ProblemID = ProblemID)
        #elimination of DOF from corner left/bottom/front (corner_lbf) -> corner left/bottom/behind (corner_lbd) 
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[4]], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_lbf,-0.5*dz, dtype=float)], ['corner_lbf', 'corner_lbd', 'EpsXZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[5]], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_lbf,-0.5*dz, dtype=float)], ['corner_lbf', 'corner_lbd', 'EpsYZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[2]], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_lbf,-dz, dtype=float)    ], ['corner_lbf', 'corner_lbd', 'EpsZZ_corner'], ProblemID = ProblemID)
        #elimination of DOF from corner right/top/behind (corner_rtd) -> corner left/bottom/behind (corner_lbd) 
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0],VarEps[3]], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtd,-dx, dtype=float)    , np.full_like(corner_rtd,-0.5*dy, dtype=float)], ['corner_rtd', 'corner_lbd', 'EpsXX_corner', 'EpsXY_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3],VarEps[1]], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtd,-0.5*dx, dtype=float), np.full_like(corner_rtd,-dy, dtype=float)    ], ['corner_rtd', 'corner_lbd', 'EpsXY_corner', 'EpsYY_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4],VarEps[5]], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtd,-0.5*dx, dtype=float), np.full_like(corner_rtd,-0.5*dy, dtype=float)], ['corner_rtd', 'corner_lbd', 'EpsXZ_corner', 'EpsYZ_corner'], ProblemID = ProblemID)
        #elimination of DOF from corner left/top/front (corner_ltf) -> corner left/bottom/behind (corner_lbd) 
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[3],VarEps[4]], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltf,-0.5*dy, dtype=float), np.full_like(corner_ltf,-0.5*dz, dtype=float)], ['corner_ltf', 'corner_lbd', 'EpsXY_corner', 'EpsXZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[1],VarEps[5]], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltf,-dy, dtype=float)    , np.full_like(corner_ltf,-0.5*dz, dtype=float)], ['corner_ltf', 'corner_lbd', 'EpsYY_corner', 'EpsYZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[5],VarEps[2]], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1), np.full_like(corner_ltf,-0.5*dy, dtype=float), np.full_like(corner_ltf,-dz, dtype=float)    ], ['corner_ltf', 'corner_lbd', 'EpsYZ_corner', 'EpsYY_corner'], ProblemID = ProblemID)
        #elimination of DOF from corner right/bottom/front (corner_rbf) -> corner left/bottom/behind (corner_lbd) 
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0],VarEps[4]], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbf,-dx, dtype=float)    , np.full_like(corner_rbf,-0.5*dz, dtype=float)], ['corner_rbf', 'corner_lbd', 'EpsXX_corner', 'EpsXZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3],VarEps[5]], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbf,-0.5*dx, dtype=float), np.full_like(corner_rbf,-0.5*dz, dtype=float)], ['corner_rbf', 'corner_lbd', 'EpsXY_corner', 'EpsYZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4],VarEps[2]], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rbf,-0.5*dx, dtype=float), np.full_like(corner_rbf,-dz, dtype=float)    ], ['corner_rbf', 'corner_lbd', 'EpsXX_corner', 'EpsZZ_corner'], ProblemID = ProblemID)
        
        #elimination of DOF from corner right/top/front (corner_rtf) -> corner left/bottom/behind (corner_lbd) 
        BoundaryCondition('MPC', ['DispX','DispX',VarEps[0],VarEps[3], VarEps[4]], 
                                 [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtf,-dx, dtype=float)    , np.full_like(corner_rtf,-0.5*dy, dtype=float), np.full_like(corner_rtf,-0.5*dz, dtype=float)], 
                                 ['corner_rtf', 'corner_lbd', 'EpsXX_corner', 'EpsXY_corner', 'EpsXZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispY','DispY',VarEps[3],VarEps[1], VarEps[5]], 
                                 [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtf,-0.5*dx, dtype=float), np.full_like(corner_rtf,-dy, dtype=float)    , np.full_like(corner_rtf,-0.5*dz, dtype=float)], 
                                 ['corner_rtf', 'corner_lbd', 'EpsXY_corner', 'EpsYY_corner', 'EpsYZ_corner'], ProblemID = ProblemID)
        BoundaryCondition('MPC', ['DispZ','DispZ',VarEps[4],VarEps[5], VarEps[2]], 
                                 [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1), np.full_like(corner_rtf,-0.5*dx, dtype=float), np.full_like(corner_rtf,-0.5*dy, dtype=float), np.full_like(corner_rtf,-dz, dtype=float)    ], 
                                 ['corner_rtf', 'corner_lbd', 'EpsXZ_corner', 'EpsYZ_corner', 'EpsZZ_corner'], ProblemID = ProblemID)

        #if rot DOF are used, apply continuity of the rotational dof
        list_rot_var = []
        if 'RotX' in ModelingSpace.ListVariable(): list_rot_var.append('RotX')
        if 'RotY' in ModelingSpace.ListVariable(): list_rot_var.append('RotY')
        if 'RotZ' in ModelingSpace.ListVariable(): list_rot_var.append('RotZ')
        
        for var in list_rot_var: 
            #### FACES ####
            BoundaryCondition('MPC', [var,var], [np.full_like(right,1), np.full_like(left,-1)], ['right','left'], ProblemID = ProblemID)
            BoundaryCondition('MPC', [var,var], [np.full_like(top,1), np.full_like(bottom,-1)], ['top','bottom'], ProblemID = ProblemID)
            BoundaryCondition('MPC', [var,var], [np.full_like(front,1), np.full_like(behind,-1)], ['front','behind'], ProblemID = ProblemID)
                     
            #### EDGES ####
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_lt,1), np.full_like(edge_lb,-1)], ['edge_lt', 'edge_lb'], ProblemID = ProblemID)        
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_rb,1), np.full_like(edge_lb,-1)], ['edge_rb', 'edge_lb'], ProblemID = ProblemID)        
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_rt,1), np.full_like(edge_lb,-1)], ['edge_rt', 'edge_lb'], ProblemID = ProblemID)        
            
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_td,1), np.full_like(edge_bd,-1)], ['edge_td', 'edge_bd'], ProblemID = ProblemID)        
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_bf,1), np.full_like(edge_bd,-1)], ['edge_bf', 'edge_bd'], ProblemID = ProblemID)        
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_tf,1), np.full_like(edge_bd,-1)], ['edge_tf', 'edge_bd'], ProblemID = ProblemID)        

            BoundaryCondition('MPC', [var,var], [np.full_like(edge_rd,1), np.full_like(edge_ld,-1)], ['edge_rd', 'edge_ld'], ProblemID = ProblemID)        
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_lf,1), np.full_like(edge_ld,-1)], ['edge_lf', 'edge_ld'], ProblemID = ProblemID)        
            BoundaryCondition('MPC', [var,var], [np.full_like(edge_rf,1), np.full_like(edge_ld,-1)], ['edge_rf', 'edge_ld'], ProblemID = ProblemID)        
                           
            #### CORNERS ####
            BoundaryCondition('MPC', [var,var], [np.full_like(corner_rbd,1), np.full_like(corner_lbd,-1)], ['corner_rbd', 'corner_lbd'], ProblemID = ProblemID)                       
            BoundaryCondition('MPC', [var,var], [np.full_like(corner_ltd,1), np.full_like(corner_lbd,-1)], ['corner_ltd', 'corner_lbd'], ProblemID = ProblemID)                        
            BoundaryCondition('MPC', [var,var], [np.full_like(corner_lbf,1), np.full_like(corner_lbd,-1)], ['corner_lbf', 'corner_lbd'], ProblemID = ProblemID)            
            BoundaryCondition('MPC', [var,var], [np.full_like(corner_rtd,1), np.full_like(corner_lbd,-1)], ['corner_rtd', 'corner_lbd'], ProblemID = ProblemID)
            BoundaryCondition('MPC', [var,var], [np.full_like(corner_ltf,1), np.full_like(corner_lbd,-1)], ['corner_ltf', 'corner_lbd'], ProblemID = ProblemID)            
            BoundaryCondition('MPC', [var,var], [np.full_like(corner_rbf,1), np.full_like(corner_lbd,-1)], ['corner_rbf', 'corner_lbd'], ProblemID = ProblemID)
            BoundaryCondition('MPC', [var,var], [np.full_like(corner_rtf,1), np.full_like(corner_lbd,-1)], ['corner_rtf', 'corner_lbd'], ProblemID = ProblemID)
                                    
        
