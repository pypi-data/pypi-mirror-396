import numpy as np
import numba as nb
from numba import jit, objmode, types
from scipy.stats import rankdata
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Calculate number of points in radius
@jit(nopython=True)
def _point_in_radius(dm, sort_idx, win_size, n):
  idx = np.ones((win_size,n), dtype = np.int64)
  for i in range(win_size):
    pre_distance = -1
    point_count = n
    for j in range(n-1, -1, -1):
      obv_point = sort_idx[i][j]
      if dm[i][obv_point] != pre_distance:
        point_count = j
        pre_distance = dm[i][obv_point]
      idx[i][obv_point] = point_count
  return idx

# Calculate mass ratio matrix
@jit(nopython=True)
def _CalMassratio(Data):
  # Beware of large numbers, it might overflow python int
    n = len(Data)
    win_size = n

    with objmode(window_dm = "i8[:, :]", sort_idx = "i8[:, :]"):
      window_dm = cdist(Data, Data)
      sort_idx = np.argsort(window_dm)

    # when pairwise distance is same, the index is also same
    current_idx = _point_in_radius(window_dm, sort_idx, win_size, n)

    count = np.zeros(win_size, dtype=np.int32)
    mass = np.zeros((win_size, n-1))

    # calculate all points
    for i in range(n):
      with objmode(dm = "i8[:, :]", remain_idx = "i8[:, :]"):
        dm = cdist([Data[i]], Data)
        remain_idx = np.argsort(dm)

      # when pairwise distance is same, the index is also same
      idx = _point_in_radius(dm, remain_idx, 1, n)

      for j in range(n):
        if i == j:
          continue
        m = (idx[0][j] + 1.0) / (current_idx[j][i] + 1.0 )
        mass[j,count[j]] = m
        count[j] += 1

    return mass

# Calculate variance mass ratio
@jit(nopython=True)
def _Var_Massratio(Data,window):
  # Beware of large numbers, it might overflow python int
    n = len(Data)
    mass = np.zeros(n)
    mass2 = np.zeros(n)
    assert(window > 0)

    # slicing window through data
    for start_point in range(0,n,window):
      stop_point = min(start_point+ window, n)
      Current_Data = Data[start_point : stop_point]
      win_size = stop_point - start_point

      with objmode(window_dm = "i8[:, :]", sort_idx = "i8[:, :]"):
        window_dm = cdist(Current_Data, Data)
        sort_idx = np.argsort(window_dm)

      # when pairwise distance is same, the index is also same
      current_idx = _point_in_radius(window_dm, sort_idx, win_size, n)

      # calculate all current points
      for i in range(start_point, stop_point):
        for j in range(i+1, stop_point):
          m = (current_idx[j%window][i]*1.0 + 1)/ (current_idx[i%window][j] + 1)
          mass[i] += m
          mass2[i] += m**2
          mass[j] += 1/m
          mass2[j] += 1/m**2

      # calculate remaining points
      for i in range(stop_point,n):
        with objmode(dm = "i8[:, :]", sort_remain = "i8[:, :]"):
          dm = cdist([Data[i]], Data)
          sort_remain = np.argsort(dm)

        # when pairwise distance is same, the index is also same
        idx = _point_in_radius(dm, sort_remain, 1, n)

        for j in range(start_point, stop_point):
          m = (current_idx[j%window][i]*1.0 + 1 )/ (idx[0][j] + 1)
          mass[i] += m
          mass2[i] += m**2
          mass[j] += 1/m
          mass2[j] += 1/m**2

    var = mass2/(n-1)-(mass/(n-1))**2
    return var

class MOF:
  '''
  Mass ratio variance-based outlier factor (MOF)
  the outlier score of each data point is called MOF.
  It measures the global deviation of density given sample with respect to other data points.
  it is global in the outlier score depend on how isolated
  data point is with respect to all data points in the data set.
  the variance of mass ratio can identify data points that have a substantially
  lower density compared to other data points.
  These are considered outliers.
  '''
  # Parameters-free
  # ----------
  def __init__(self):
    self.name='MOF'
    self.Data = []
    self.MassRatio = []

  def fit(self,Data, Window = 10000, KeepMassRatio = True):

    '''
    Parameters
    ----------
    Data : numpy array of shape (n_samples, n_features)
        The input samples.
    window : integer (int)
        Window size for calculation.
        default window size is 10000.
    KeepMassRatio : boolean
        All points' mass ratio are kept when an argument is True. Beware for memory limitaion.
        Can be set to False for exploding memory.
        default KeepMassRatio size is True.
    '''
    '''
    Returns
    -------
    self : object
    '''
#  Fitted estimator.
    self.Data =Data

# Calculate mass ratio variance (MOF)
    if KeepMassRatio:

      print("Keeping mass ratio")
      self.MassRatio = _CalMassratio(Data)

      # calculate scores
      scores = np.zeros(Data.shape[0])
      for i in range(Data.shape[0]):
        arr = self.MassRatio[i]
        scores[i] = np.var(arr)
      
      self.decision_scores_ = scores

    else:
      # calculate scores
      self.decision_scores_= _Var_Massratio(Data,Window)

# ----------------
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
