import pandas as pd
import matplotlib.pyplot as plt

def plot_npp():
    df = pd.read_csv('ORCA_NPP_Quarterly_Indian_Coast.csv')
    df_mean = df.groupby(['latitude', 'longitude'])['NPP'].mean().reset_index()
    pivot_df = df_mean.pivot(index='latitude', columns='longitude', values='NPP')

    plt.figure(figsize=(10, 8))
    plt.pcolormesh(pivot_df.columns, pivot_df.index, pivot_df.values, cmap='YlGn', shading='auto')
    plt.title('Average Net Primary Production (NPP) - Indian Coast (2012-2024)')
    plt.colorbar(label='NPP (mg C / m2 / day)')
    plt.tight_layout()
    plt.savefig('Map_NPP.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved plot to Map_NPP.png")

if __name__ == "__main__":
    plot_npp()
