import sys
import datetime
import pandas as pd
import random as rnd
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import minimize
from scipy.optimize import differential_evolution

#########################################################
# Loading data
#########################################################
initial_data = pd.read_excel(
    "Worktables_TS.xlsx", "features2", skiprows=[0, 1], drop=True)
initial_data.fillna("NA", inplace=True)
filtered_data = initial_data.copy()

# Subtracting off the minimum score of 10  - it is assigned to the default fields "Passport" and "National_ID"
target_TS = initial_data["Target"].copy()
target_TS -= 10
weights = initial_data["Frequency"].copy()


# Renaming things to make them understandable
filtered_data.rename(index=str, inplace=True,
                     columns={"Unnamed: 4": "Passport", "Unnamed: 5": "National_ID", "Unnamed: 15": "Single",
                              "Unnamed: 16": "Relationship", "Unnamed: 18": "Raising_children",
                              "Unnamed: 19": "Have_grandchildren", "Unnamed: 21": "Not_educated",
                              "Unnamed: 22": "Elementary", "Unnamed: 23": "Secondary", "Unnamed: 24": "Bachelor",
                              "Unnamed: 25": "Master", "Unnamed: 26": "PhD_Doctorate", "Unnamed: 28": "Employment_None",
                              "Unnamed: 29": "Employed", "Unnamed: 30": "Self_Employed", "Unnamed: 31": "Retired",
                              "Unnamed: 32": "Student"})
filtered_data.fillna("NA", inplace=True)
############################################################
# Adding and combining relevant fields
############################################################

# Merging PhD and Master (too few PhDs)
filtered_data["Post_graduate"] = filtered_data.apply(
    lambda x: 1 if x['PhD_Doctorate'] == 1 or x["Master"] == 1 else 0, axis=1)

# Categories dealing with education
ed_categories = ['PhD_Doctorate', "Master", "Bachelor",
                 "Secondary", "Elementary", "Not_educated"]
# Separating the different levels of education
separate_education = True
if separate_education:
    for i in range(len(ed_categories)):
        for j in range(i + 1, len(ed_categories)):
            filtered_data[ed_categories[j]] = filtered_data.apply(
                lambda x: 0 if x[ed_categories[i]] == 1 else x[ed_categories[j]], axis=1)

# Clumping together the employment variables which are infrequent: Self_Employed (6), Retired (2), Student (2)
filtered_data["Employment_other"] = filtered_data.apply(lambda x: 1 if (x["Self_Employed"] == 1
                                                                        or x["Retired"] == 1 or x["Student"] == 1) else 0, axis=1)

# ## Don't do - it is a step backwards rather than forwards
# filtered_data["$0-$1000"] = filtered_data.Income.apply(
#     lambda x: 1.0 if 0.0 <= x < 1000 else 0.0)
# filtered_data["$1000-$2000"] = filtered_data.Income.apply(
#     lambda x: 1.0 if 1000.0 <= x < 2000 else 0.0)
# filtered_data["$2000-$4000"] = filtered_data.Income.apply(
#     lambda x: 1.0 if 2000.0 <= x < 4000 else 0.0)
# filtered_data["$4000-$8000"] = filtered_data.Income.apply(
#     lambda x: 1.0 if 4000.0 <= x < 8000 else 0.0)
# filtered_data["$8000-$16000"] = filtered_data.Income.apply(
#     lambda x: 1.0 if 8000.0 <= x < 16000 else 0.0)
# filtered_data["$16000-$32000"] = filtered_data.Income.apply(
#     lambda x: 1.0 if 16000.0 <= x < 32000 else 0.0)
# filtered_data["$32000+"] = filtered_data.Income.apply(
#     lambda x: 1.0 if 32000.0 <= x else 0.0)
# # Clumping together 16000 - 32000 and 32000+ (too few 32000+)
# filtered_data["$16000+"] = filtered_data.Income.apply(lambda x: 1.0 if 16000 <= x else 0.0)

#sys.exit()
##########################################################################
# Choosing the categories relevant for the inversion
##########################################################################
inversion_df = filtered_data[[#"$0-$1000",
                              #"$1000-$2000",
                              #"$2000-$4000",
                              #"$4000-$8000",
                              #"$8000-$16000",
                              #"$16000-$32000",
                              #"$32000+",
                              "Age",
                              "Bachelor",
                              "Bank_account",
                              "Bank_reference",
                              #"Citizenship", - not for optimization
                              #"Country",   - not for optimization
                              "Credit_card_holder",
                              "Credit_history",
                              "Elementary",
                              "Employed",
                              "Employment_other",
                              "Has_license",
                              "Have_grandchildren",
                              "Income",
                              "Income_source_declared",
                              "Insurance",
                              "Investor",
                              #"Occupation", - field covered by Employed and Employment_other
                              "Phone",
                              "Post_graduate",
                              "Proof_of_residence",
                              "Raising_children",
                              "Relationship",
                              "Secondary",
                              "Site",
                              "Social_network_account",
                              "Stable_income",
                              "Stake",
                              "ZIP_code"]]

########################################################################
# Building cost functions
########################################################################
def predict_TS(y: list):
    # Arranged as per the data
    predicted_TS = inversion_df.apply(lambda x: x.dot(y), axis=1)
    return predicted_TS


def minimize_me(y: list):
    features = inversion_df.columns.tolist()

    ############## Expectations ################
    # Positive/Negative demands:
    penalties = [0 for x in features]

    # Returning a high penalty for wrong signs
    signs = {k: 1 for k in features}
    for k, v in signs.items():
        ind = features.index(k)
        penalties[ind] += 10 if y[ind] * v < 0 else 0

    # # # Setting bounding boxes
    bnd_boxes = [(0, 30) for k in range(len(init_guess))]
    for i in range(len(y)):
        penalties[i] += 10 if y[i] < bnd_boxes[i][0] or y[i] > bnd_boxes[i][1] else 0

    # relative size demands:
    # cchold_ind = features.index('Credit_card_holder')
    # cchold_weight = y[cchold_ind]
    # cchist_ind = features.index('Credit_history')
    # cchist_weight = y[cchist_ind]
    # if cchold_weight > cchist_weight:
    #     return 1000000

    predicted_TS = predict_TS(y)
    TS_error = target_TS.values - predicted_TS.values
    # Using L2 norm error as cost
    return pd.np.square(TS_error).sum()


########################################################################
# Regression / fitting
########################################################################
regressed = linear_model.LinearRegression(fit_intercept=False)
regressed.fit(inversion_df.values, target_TS.values,
              sample_weight=weights.values)

weightings = dict()
print("_________________________________________________")
for i in range(len(inversion_df.columns)):
    weightings[inversion_df.columns[i]] = regressed.coef_[i]
    print("{:>22}".format(inversion_df.columns[i]), ":\t", regressed.coef_[i])

bnd_boxes = [(0, 2 * max(regressed.coef_))
             for k in range(len(inversion_df.columns))]
init_guess = [abs(x) for x in regressed.coef_]

simp_result = minimize(fun=minimize_me, x0=init_guess,
                       method="Nelder-Mead", options={"maxiter": 100000})
print("Simp Success = " + str(simp_result.success))
print("Simp Message = " + str(simp_result.message))

DE_result = differential_evolution(minimize_me, bnd_boxes, strategy='best1bin', maxiter=7500, popsize=15, tol=0.01, mutation=(
    0.5, 1), recombination=0.7, seed=None, callback=None, disp=True, polish=False, init='latinhypercube')
print("DE Success = " + str(DE_result.success))
print("DE Message = " + str(DE_result.message))


print("_________________________________________________")
print("{:>22}\t{:>10}\t{:>10}\t{:>10}\t{:>10}".format(
    "Parameter", "Unbounded LSq", "Initial_guess", "Simplex", "DE"))
for i in range(len(inversion_df.columns)):
    print("{:>22}\t{:10.9f}\t{:10.9f}\t{:10.9f}\t{:10.9f}".format(
        inversion_df.columns[i], regressed.coef_[i], init_guess[i], simp_result.x[i], DE_result.x[i]))
print("________________________________________________")
print("Costs: ", minimize_me(regressed.coef_), " , ",  minimize_me(init_guess), " , ",
      minimize_me(simp_result.x), " , ", minimize_me(DE_result.x))


##################################################################################
# Comparing results to First ITSA
##################################################################################
results_2_DF = pd.DataFrame()
results_2_DF["Target_TS"] = initial_data.Target
results_2_DF["Unbounded_TS"] = (predict_TS(regressed.coef_) + 10).values
results_2_DF["Simplex_TS"] = (predict_TS(simp_result.x) + 10).values
results_2_DF["DE_TS"] = (predict_TS(DE_result.x) + 10).values

results_2_DF.to_csv("./regression_2_results.csv", index=False)

results_DF = pd.DataFrame(columns=["Parameters",  "Unbounded_regression",
                                   "Simplex_regression",   "DE_regression"])
results_DF["Parameters"] = inversion_df.columns
results_DF["Unbounded_regression"] = regressed.coef_
results_DF["Simplex_regression"] = simp_result.x
results_DF["DE_regression"] = DE_result.x
results_DF = results_DF.append({"Parameters": "Cost", "Unbounded_regression": minimize_me(regressed.coef_),
                                "Simplex_regression": simp_result.fun, "DE_regression": DE_result.fun},
                               ignore_index=True)

results_DF.to_csv("./regression_results.csv", index=False)
