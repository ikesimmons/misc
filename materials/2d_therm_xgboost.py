"""
Example script to train and evaluate an XGBoost regressor for predicting
the heat of formation (hform) from molecular feature data.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
from itertools import permutations

def main():

    # Load the data
    test_df = pd.read_json('data/test.json')
    train_df = pd.read_json('data/train.json')

    def expand_atoms_dict(atoms_dict):
        """
        Given a dict like:
        
        {
            'numbers': [...],
            'positions': [[x,y,z], ...],
            'cell': [[x,y,z], ...],
            'pbc': [bool,bool,bool],
            ...
        }
        
        returns a flattened dict of key-value pairs like:
        
        {
            'atom_0': <number>,
            'atom_1': <number>,
            ...
            'atom_0_x': <float>,
            'atom_0_y': <float>,
            'atom_0_z': <float>,
            ...
            'cell_0_x': <float>,
            ...
            'pbc_x': <bool>,
            'pbc_y': <bool>,
            'pbc_z': <bool>,
            ...
        }
        """
        if not isinstance(atoms_dict, dict):
            # Handle null or non-dict values gracefully
            return {}
        
        row = {}
        
        # ---------------------
        # 1) numbers -> atom_0, atom_1, ...
        # ---------------------
        numbers = atoms_dict.get('numbers', [])
        # ---------------------
        # 2) positions -> atom_0_x, atom_0_y, atom_0_z, ...
        # ---------------------
        positions = atoms_dict.get('positions', [])
        
        row = {}
        
        # 1) numbers -> atom_0, atom_1, ...
        for i, number in enumerate(numbers):
            row[f'atom_{i}'] = number

        for i, coords in enumerate(positions):
            # Ensure each coords has at least length 3 to avoid index errors
            x, y, z = (coords + [None, None, None])[:3]
            row[f'atom_{i}_x'] = x
            row[f'atom_{i}_y'] = y
            row[f'atom_{i}_z'] = z
            
        # ---------------------
        # 2) positions -> atom_0_x, atom_0_y, atom_0_z, ...
        # ---------------------
        positions = atoms_dict.get('positions', [])
        for i, coords in enumerate(positions):
            # Ensure each coords has at least length 3 to avoid index errors
            x, y, z = (coords + [None, None, None])[:3]
            row[f'atom_{i}_x'] = x
            row[f'atom_{i}_y'] = y
            row[f'atom_{i}_z'] = z
            
        # ---------------------
        # 3) cell -> cell_0_x, cell_0_y, cell_0_z, ...
        # ---------------------
        cell = atoms_dict.get('cell', [])
        cell_axes = ['a', 'b', 'c']
        for i, ccoords in enumerate(cell):
            axis = cell_axes[i] if i < len(cell_axes) else str(i)
            x, y, z = (ccoords + [None, None, None])[:3]
            row[f'cell_{axis}_x'] = x
            row[f'cell_{axis}_y'] = y
            row[f'cell_{axis}_z'] = z
            
        # ---------------------
        # 4) pbc -> pbc_x, pbc_y, pbc_z, ...
        #    (Assuming pbc has up to 3 elements)
        # ---------------------
        pbc = atoms_dict.get('pbc', [])
        pbc_axes = ['x', 'y', 'z']
        for i, flag in enumerate(pbc):
            axis = pbc_axes[i] if i < len(pbc_axes) else str(i)
            row[f'pbc_{axis}'] = bool(flag) if flag is not None else False
        return row

    df_expanded = pd.DataFrame([expand_atoms_dict(train_df['atoms'].iloc[0])])
    df_train_result = train_df.drop(columns=['atoms']).join(df_expanded)

    # 1. Load dataset
    # -------------------------------------------------------------------------
    # Replace 'molecule_data.csv' with the path to your dataset.
    df = df_train_result
    
    # If your dataset has columns you don't want to use (e.g. IDs, strings),
    # either drop them or filter them out here.
    # Example:
    # df.drop(columns=["ID", "Name"], inplace=True)
    
    # 2. Separate features (X) and target (y)
    # -------------------------------------------------------------------------
    # Assuming 'hform' is the name of the column in df that contains
    # the heat of formation.
    y = df["hform"]
    X = df.drop(columns=["hform","id","formula"])  # drop the target column from features
    
    # 3. Train-test split
    # -------------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, 
        y, 
        test_size=0.2,     # 20% of data is reserved for testing
        random_state=42    # for reproducibility
    )
    
    # 4. Define and train the XGBoost Regressor
    # -------------------------------------------------------------------------
    # You can tune hyperparameters here. Below are just default parameters as a start.
    xgb_model = XGBRegressor(
        n_estimators=100,        # number of trees
        learning_rate=0.1,       # step size shrinkage
        max_depth=6,             # maximum tree depth
        subsample=1.0,           # fraction of samples used for each tree
        colsample_bytree=1.0,    # fraction of features used for each tree
        random_state=42
    )
    
    xgb_model.fit(X_train, y_train)
    
    # 5. Evaluate the model
    # -------------------------------------------------------------------------
    y_pred = xgb_model.predict(X_test)
    
    # Calculate Mean Squared Error and R^2
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("Model performance on test set:")
    print(f" - Mean Squared Error (MSE): {mse:.4f}")
    print(f" - R^2 Score:               {r2:.4f}")

    # 6. (Optional) Feature importance analysis
    # -------------------------------------------------------------------------
    # XGBoost provides a feature_importances_ attribute after fitting.
    importances = xgb_model.feature_importances_
    feature_names = X.columns

    # Sort feature importances in descending order, along with their names
    sorted_indices = np.argsort(importances)[::-1]
    print("\nFeature Importances (descending):")
    for idx in sorted_indices:
        print(f"{feature_names[idx]}: {importances[idx]:.4f}")

if __name__ == "__main__":
    main()