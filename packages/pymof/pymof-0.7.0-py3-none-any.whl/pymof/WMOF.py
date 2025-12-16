import numpy as np
import numba as nb
from numba import jit, objmode, types
from scipy.stats import rankdata
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from .MOF import _Var_Massratio

# Calculate windowing mass ratio
@jit(nopython=True)
def _Window_Massratio(Data,Window,Overlap_ratio):
  n =Data.shape[0]
  scores = np.zeros(n)

  assert(Window > 0 )
  assert(0.0 <= Overlap_ratio <= 0.5)

  overlap_size = int(Overlap_ratio * Window)
  mid_overlap_point = int(Window - overlap_size/2)
  score_count = 0

  # Windowing data and send to MOF
  for start_point in range(0, n , Window - overlap_size):
    stop_point = min(n, start_point + Window)
    w = stop_point - start_point
    current_data = Data[start_point : stop_point]
    # Last data window size (w) <= Window
    current_scores = _Var_Massratio(current_data,w)

    # Assign score to data points
    stop_score_count = min(n, start_point + mid_overlap_point)
    for i in range(score_count, stop_score_count):
      scores[i] = current_scores[i - start_point]
      score_count += 1

  return scores

# Calculate stream windowing mass ratio
@jit(nopython=True)
def _Stream_Window_Massratio(Data, Window, Overlap_ratio, Start_idx):
  n =Data.shape[0]
  scores = np.zeros(n)

  assert(Window > 0 )
  assert(0.0 <= Overlap_ratio <= 0.5)

  mid_overlap_point = int((1 - Overlap_ratio/2) * Window)
  scores = _Var_Massratio(Data,Window)

  return mid_overlap_point - int((1 - Overlap_ratio) * Window), Window - int((1 - Overlap_ratio) * Window), scores[Start_idx : mid_overlap_point] # start_idx, len, scores

class WMOF:

# Windowing mass-ratio-variance based outlier factor (WMOF)
# This algorithm is an extension of the mass-ratio-variance outlier factor algorithm (MOF).
# WMOF operates on overlapping windows of fixed size, specified by the user.
# The use of overlapping windows ensures that anomalies occurring at window boundaries are not missed.
# For each window, the MOF score is computed for all data points within the window.

# Parameters-free
# ----------
  def __init__(self, window=1000, overlap_ratio = 0.2):
    self.name='WMOF'
    self.data = []
    self._DataCount = 0
    self._start_index = 0
    self.window_size = window
    self.overlap_ratio = overlap_ratio
    self.decision_scores_ = np.array([], dtype = np.float64)
    self.anomaly = np.array([])

  def fit(self,data):

    '''
    Parameters
    ----------
    data : numpy array of shape (n_samples, n_features)
        The input samples.
    '''
    '''
    Returns
    -------
    self : object
    '''

  #  Fitted estimator.
    self.data = data

  # Calculate Windowing mass ratio variance (WMOF)
    self.decision_scores_= _Window_Massratio(data,self.window_size,self.overlap_ratio)
    return self

  def fit_score(self, x):
    '''
    Parameters
    ----------
    x : numpy array of shape (1, n_features)
        A new input data point.
    '''
    '''
    Returns
    -------
    score : numpy array of shape ((1 - overlap_ratio) * Window)
        A batch decision scores for the current window.
    '''
    self.data.append(x)
    self._DataCount += 1
    score = []
    if self._DataCount == self.window_size:

      self._start_index, self._DataCount, score =  _Stream_Window_Massratio(np.array(self.data), self.window_size, self.overlap_ratio, self._start_index)
      self.data = self.data[int((1 - self.overlap_ratio) * self.window_size):]

    return score

  def fit_last_score(self):
    '''
    Parameters
    ----------
    '''
    '''
    Returns
    -------
    score : numpy array of shape ((1 - overlap_ratio) * Window,)
        decision scores for remaining points in the last window.
    '''
    self._start_index, self._DataCount, score =  _Stream_Window_Massratio(np.array(self.data), len(self.data), 0, self._start_index)
    self.data = self.data[int((1 - self.overlap_ratio) * self.window_size):]

    return score

  def detectAnomaly(self, threshold):
    '''
    Parameters
    ----------
    threshold : float
        A threshold value for detect anomaly points.
    '''
    '''
    Returns
    -------
    idx : numpy array of shape (n_samples,)
        An index array of anomaly points in data.
    '''
    # Check data avaliablity
    assert(len(self.data) != 0)

    if self.decision_scores_.shape[0] == 0:
      self.fit(self.data)
    idx = np.squeeze(np.argwhere(self.decision_scores_ > threshold))
    self.anomaly = np.append(self.anomaly,idx).astype(np.int32)
    self.anomaly = np.unique(self.anomaly)

    return idx

  def detectStream(self, scores, tau = None, n = 0.01):
    '''
    Parameters
    ----------
    scores : numpy array of shape (n_samples,)
        decision scores for the current window.
    tau : float
        A threshold value for detecting anomaly points.
        default tau is None, the threshold is determined by 'n'.
    n : float or int
        If float (0.01 <= n <= 0.49), it is the percentage of anomaly data points
        to select (e.g., 0.01 means the top 1% of scores).
        If int, it is the exact number of anomaly data points to select.
        default n is 0.01
    '''
    '''
    Returns
    -------
    idx : numpy array of shape (n_samples,)
        An index array of anomaly points in the current window of data.
    '''
    # Check data availability
    assert(len(self.data) != 0)

    # Ensure decision scores are available (by fitting if necessary)
    if len(scores) == 0:
      return np.array([])
      
    num_data_points = scores.shape[0]
    
    # 1. Check tau first
    if tau is not None:
      threshold = tau
      
    # 2. If tau is None, check n (integer or float)
    elif type(n) == int:
      k = min(n, num_data_points) # Number of anomalies to pick
      if k == 0:
          threshold = np.max(scores) + 1
      else:
          threshold = np.percentile(scores, 100 * (num_data_points - k) / num_data_points)
          
    elif type(n) == float:
      percentile_cutoff = 100 * (1.0 - n)
      if 100 < percentile_cutoff or percentile_cutoff <  50: # Check for safety if n > 0.5
          percentile_cutoff = 100

      threshold = np.percentile(scores, percentile_cutoff)
      
    else:
      threshold = np.max(scores) + 1 # Threshold that excludes all points
      
    idx = np.squeeze(np.argwhere(scores > threshold))
    
    if idx.ndim == 0:
        idx = np.array([idx])

    return idx