The order of execution is prompted by file names.
<ul>
  <li>_1_loadTraslate.py: to load tweets of users form txt(or csv) raw files and translate sentences in to English;</li>
  <li>_3_text2words.py:   to remove meaningless symbols and tokenize tweets into word lists, as well as record them into txt files for LDA later;</li>
  <li>_4_afterLDA.py:     to load the result of TwitterLDA into npy files;</li>
  <li>_5_tiPartition.py:  to divide the message stream into sessions;</li>
</ul>
