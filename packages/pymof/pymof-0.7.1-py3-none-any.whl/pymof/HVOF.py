import numpy as np
import numba as nb
from numba import jit, objmode, types
from scipy.stats import rankdata
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Calculate hypervolume ratio matrix
@jit(nopython=True)
def _CalVolumeRatio(Data, mass_k = 1):
  # Beware of large numbers, it might overflow python int
    n = len(Data)
    win_size = n

    with objmode(window_dm = "f8[:, :]", sort_idx = "i8[:, :]"):
      window_dm = cdist(Data, Data)
      # print(window_dm)
      sort_idx = np.argsort(window_dm)
      # print(sort_idx)

    # when pairwise distance is same, the index is also same
    mass = np.zeros((win_size, n-1), dtype=np.float32)

    # calculate all points
    for i in range(n):
      r_p = window_dm[i][sort_idx[i][mass_k]]
      # print("i =",i,r_p)
      count = 0
      for j in range(n):
        if i == j:
          continue

        r_q = window_dm[j][sort_idx[j][mass_k]]
        mass[i,count] =  r_p/r_q 
        count += 1
    # print(mass)

    return mass

# Calculate hypervolume ratio variance
@jit(nopython=True)
def _Var_VolumeRatio(Data, mass_k  = 1, Window = 1000):

  n = len(Data)
  radius_k = np.zeros(n, dtype=np.float32)

  for i in range(0, n, Window):
    stop_idx = min(i+Window, n)

    with objmode(window_dm = "f8[:, :]", sort_idx = "i8[:, :]"):
      window_dm = cdist(Data[i: stop_idx], Data)
      # print(window_dm)
      sort_idx = np.argsort(window_dm)
      # print(sort_idx)
    
    actual_size = stop_idx - i
    for j in range(actual_size):
      idx = i + j
      radius_k[idx] = window_dm[j][sort_idx[j][mass_k]]
      # print(radius_k)

  inv_radius = radius_k**-1
  sum_inv_radius = np.sum(inv_radius)
  s2_inv_radius = np.sum(inv_radius**2)

  VarVolumeRatio2 = np.zeros(n, dtype=np.float32)
  for i in range(n):
    VarVolumeRatio2[i] = (s2_inv_radius - inv_radius[i]**2)/(n-1)  - ((sum_inv_radius - inv_radius[i])/(n-1))**2
    VarVolumeRatio2[i] *= radius_k[i]**2
  
  return VarVolumeRatio2


class HVOF:
  '''
  Hypervolume-ratio-variance outlier factor (HVOF)
  The hypervolume ratio of the computed data point is defined as the ratio of the hypervolume from data points 
  within the sphere with respect to this computed data point for the fixed mass. 
  The mass is defined as the number of data points within the sphere.
  '''
  def __init__(self):
    self.name='HVOF'
    self.Data = []
    self.VolumeRatio = []

  def fit(self,Data, mass_k = 2, Window = 10000, KeepVolumeRatio = True):

    '''
    Parameters
    ----------
    Data : numpy array of shape (n_samples, n_features)
        The input samples.
        
    mass_k : int
        Number of nearest neighbors to consider when calculating the hypervolume (the "mass").
        
    Window : int
        Window size for calculation when `KeepVolumeRatio` is False.
        (Default is 10000)
        
    KeepVolumeRatio : bool
        If True, the individual hypervolume ratio for all points are calculated and stored.
        Warning: May lead to high memory usage.
        Can be set to False to avoid memory issues (will use the `Window` parameter).
        (Default is True)
        
    Returns
    -------
    self : object
    '''
    #  Fitted estimator.
    self.Data = Data

    # Calculate hyper volume ratio variance (HVOF)
    if mass_k >= 2:
      mass_k -= 1
    elif mass_k >= len(Data):
      mass_k = len(Data) - 1
    else:
      mass_k = 1
    
    if KeepVolumeRatio:

      self.VolumeRatio = _CalVolumeRatio(Data, mass_k)

      # calculate scores
      scores = np.zeros(Data.shape[0])
      for i in range(Data.shape[0]):
        arr = self.VolumeRatio[i]
        scores[i] = np.var(arr)

      self.decision_scores_ = scores

    else:
      self.decision_scores_ = _Var_VolumeRatio(Data, mass_k, Window)


  def visualize(self):
    '''
    Parameters free
    Visualize data points
    '''
    '''
    Parameters
    ----------
    '''
    '''
    Returns
    -------
    '''
    if self.Data.shape[1] == 3:
      fig = plt.figure(figsize=(15, 15))
      ax = fig.add_subplot(111, projection='3d')
      p = ax.scatter(self.Data[:, 0], self.Data[:, 1], self.Data[:, 2], c = np.log(self.decision_scores_+0.00001), cmap='jet')
      fig.colorbar(p)
    elif self.Data.shape[1] == 2:
      fig = plt.figure(figsize=(15, 15))
      ax = fig.add_subplot()
      p = ax.scatter(self.Data[:, 0], self.Data[:, 1], c = np.log(self.decision_scores_+0.00001), cmap='jet')
      fig.colorbar(p)
    else :
      print("Cannot visualize dimension space more than 3")
    return self.decision_scores_
