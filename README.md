# Complex Topic Pattern Mining #
A new set of topic-based patterns, named Complex Topic Patterns (CTPs), by extending Sequential Topic Patterns (STPs) with time-interval constraints and the interleaving operator. The purpose of proposing CTPs is to discover users with special intentions on public social platforms on the Internet, especially, to detect Russian trolls in Twitter.

## Main Data Source ##
The raw data has been processed into several user-level message sequence databases, and the global one is separated and stored into three files: Sess_dict.npy, LDA_dict.npy, and Prob_dict.npy.
<table>
        <tr>
            <th>file</th>     <th>key_1</th>    <th>key_2</th>    <th>value</th>
        </tr>
        <tr>
            <th>Sess_dict.npy</th> <th>user id</th> <th>session id</th> <th>a series of time-stampes </th>
        </tr>
        <tr>
            <th>LDA_dict.npy</th> <th>user id</th> <th>time-stamp</th> <th>a set of topic categories</th>
        </tr>
        <tr>
            <th>Prob_dict.npy</th> <th>user id</th> <th>time-stamp</th> <th>the coorespoding set of probabilities</th>
        </tr>
</table>


## Mining Algorithms ##
Two novel algorithms for mining CTPs, interval-enhanced and patternset-interval-enhanced DP process, are described in "_3B_CTP_SEQMining_Algo.py" and "_3C_CTP_ILVMining_Algo.py" in detail,  
whereas "_3A_STP_STPMining_Algo.py" describe the baseline algorithm for mining classical sequential patterns.  
Besides that, the following algorithms are designed for user-aware rarity analysis and cross filtering.  
  
The execution order of mining algorithms refers to the file names.
<table>
        <tr>
            <th>algorithm</th>
            <th>statement</th>
        </tr>
        <tr>
            <th align="left">_3A_STP_STPMining_Algo.py</th> 
            <th align="left">mining sequential patterns which are not constrained by time-intervals.</th>
        </tr>
        <tr>
            <th align="left">_3B_CTP_SEQMining_Algo.py</th>  
            <th align="left">mining sequential patterns which satisfy one(or more than one) time-interval constraint(s).</th>
        </tr>
        <tr>
            <th align="left">_3C_CTP_ILVMining_Algo.py</th>  
            <th align="left">mining interleaving patterns which satisfy one(or more than one) time-interval constraint(s).</th>
        </tr>
        <tr>
            <th align="left">_4_file2dict2mat.py</th>  
            <th align="left">integrating all user-pattern pairs stored in different files into a big matrix.</th>
        </tr>
        <tr>
            <th align="left">_5_getURR.py</th>  
            <th align="left">calculating the index of user-aware rarity, including global support, absolute rarity, and relative rarity.</th>
        </tr>
        <tr>
            <th align="left">_6A_gridSearch.py</th>  
            <th align="left">get URSEQs and URILVs.</th>
        </tr>
        <tr>
            <th align="left">_6B_postprocessing.py</th>  
            <th align="left">get URCTPs.</th>
        </tr>
</table>








