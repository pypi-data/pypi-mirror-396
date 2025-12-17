import matplotlib.pyplot as plt
import pandas as pd


def display_dataset(df):
    """
    Creates a pretty table displaying dataset information including shape,
    data types, and unique values.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze

    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    # Gather information
    info_data = {
        "Column": df.columns.tolist(),
        "Data Type": [str(dtype) for dtype in df.dtypes],
        "Unique Values": [df[col].nunique() for col in df.columns],
    }

    info_df = pd.DataFrame(info_data)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, max(6, len(df.columns) * 0.35 + 1)))
    ax.axis("tight")
    ax.axis("off")

    # Create the table - position it lower to avoid title overlap
    table = ax.table(
        cellText=info_df.values,
        colLabels=info_df.columns,
        cellLoc="left",
        loc="upper center",
        colWidths=[0.4, 0.3, 0.3],
        bbox=[0, 0, 1, 0.95],
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Style header
    for i in range(len(info_df.columns)):
        cell = table[(0, i)]
        cell.set_facecolor("#3498db")
        cell.set_text_props(weight="bold", color="white")

    # Alternate row colors
    for i in range(1, len(info_df) + 1):
        for j in range(len(info_df.columns)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor("#ecf0f1")
            else:
                cell.set_facecolor("white")

    # Add title with dataset shape
    title_text = f"Dataset Information: {df.shape[0]:,} rows, {df.shape[1]} columns"
    plt.title(title_text, fontsize=14, fontweight="bold", pad=30, y=0.98)

    plt.tight_layout()
    plt.show()
