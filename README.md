# Complex Topic Pattern Mining #
A new set of topic-based patterns, named Complex Topic Patterns (CTPs), by extending Sequential Topic Patterns (STPs) with time-interval constraints and the interleaving operator. The p

## Main Data Source ##
The raw data has been processed into several user-level message sequence databases, and the global one is separated and stored into three files: Sess_dict.npy, LDA_dict.npy, and Prob_dict.npy.
|file         |key_1        |key_2        |value                                  |
|Sess_dict.npy|user id      |session id   |a series of time-stampes               |
|LDA_dict.npy |user id      |time-stamp   |a set of topic categories              |
|Prob_dict.npy|user id      |time-stamp   |the coorespoding set of probabilities  |



## Mining Algorithms ##
The execution order of mining algorithms refers to the file names.
<ul>
  <li>_3A_STP_STPMining_Algo.py: mining sequential patterns which are not constrained by time-intervals.</li>
  <li>_3B_CTP_SEQMining_Algo.py: mining sequential patterns which satisfy one(or more than one) time-interval constraint(s).</li>
  <li>_3C_CTP_ILVMining_Algo.py: mining interleaving patterns which satisfy one(or more than one) time-interval constraint(s).</li>
  <li>_4_file2dict2mat.py: integrating all user-pattern pairs stored in different files into a big matrix.</li>
  <li>_5_getURR.py: calculating the index of user-aware rarity, including global support, absolute rarity, and relative rarity.</li>
  <li>_6A_gridSearch.py: get URSEQs and URILVs </li>
  <li>_6B_postprocessing.py: get URCTPs </li>
</ul>


## Running Time Test ##






