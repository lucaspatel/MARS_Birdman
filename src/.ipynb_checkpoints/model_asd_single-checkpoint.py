from pkg_resources import resource_filename

import biom
# IF USING A DIFFERENT STAN MODEL, CHANGE HERE
from birdman import SingleFeatureModel
import numpy as np
import pandas as pd

# PROVIDE FILEPATH TO STAN MODEL
# ENSURE THAT YOU HAVE COMPILED THIS MODEL BY 
# ACTIVATING BIRDMAN ENVIRONMENT
# OPENING PYTHON/IPYTHON  
# IMPORTING CMDSTANPY, THEN RUNNING 
# cmdstanpy.CmdStanModel(stan_file="path/to/model.stan")
MODEL_PATH = "/home/lpatel/projects/2024-03-04_pierce-autism/scripts/MARS_Birdman/birdman/src/stan/negative_binomial_single.stan"
# REPLACE BELOW WITH YOUR METADATA 
MD = pd.read_table("/home/lpatel/projects/2024-03-04_pierce-autism/qiita/15350_20240110-175840.txt", sep="\t", index_col='sample_name')

# NAME CLASS SOMETHING RELEVANT TO YOUR MODEL
class ASDModelSingle(SingleFeatureModel):
    def __init__(
        self,
        table: biom.Table,
        feature_id: str,
        # OPTIONAL: CHANGE PARAMETERS
        beta_prior: float = 5.0,
        inv_disp_sd: float = 0.5,
        num_iter: int = 500,
        num_warmup: int = 500,
        **kwargs
    ):
        super().__init__(
            table=table,
            feature_id=feature_id,
            model_path=MODEL_PATH,
            num_iter=num_iter,
            num_warmup=num_warmup,
            **kwargs
        )


        D = table.shape[0]
        A = np.log(1 / D) 
        # REPLACE WITH YOUR PATSY STYLE FORMULA
        self.create_regression(formula="dx+gender+host_age", metadata=MD)

        param_dict = {
            "depth": np.log(table.sum(axis="sample")),
            "B_p": beta_prior,
            "inv_disp_sd": inv_disp_sd,
	    "A": A
        }
        self.add_parameters(param_dict)

        self.specify_model(
            params=["beta_var", "inv_disp"],
            dims={
                "beta_var": ["covariate"],
                "log_lhood": ["tbl_sample"],
                "y_predict": ["tbl_sample"]
            },
            coords={
                "covariate": self.colnames,
                "tbl_sample": self.sample_names,
            },
            include_observed_data=True,
            posterior_predictive="y_predict",
            log_likelihood="log_lhood"

        )
