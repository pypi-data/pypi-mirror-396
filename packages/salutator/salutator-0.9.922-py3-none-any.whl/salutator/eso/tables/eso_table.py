# my_observations = eso_archive.observations
# my_observations.colnames  # prints colnames
# my_observations = my_observations[[“target_name”, “s_ra”, “s_dec”]]  # select cols
# my_observations = my_observations[my_observations[“target_name”].lower().contains(“sgr”)] # Filter for SGRA, SGR A, SgrA, sgr_a, . . . 

# # Carry out the actual work:
# my_observations.count()
# my_observations.to_csv()
# my_observations.pprint() 


# abstract class
class EsoColumn():
    pass


class EsoTable():
    pass

