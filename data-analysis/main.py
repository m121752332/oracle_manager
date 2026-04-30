import matplotlib.pyplot as plt
import seaborn as sns

def main():

    # 載入範例資料
    df = sns.load_dataset("penguins")

    # 基本統計
    print(df.describe())

    # 視覺化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.scatterplot(data=df, x="bill_length_mm", y="bill_depth_mm", 
                    hue="species", ax=axes[0])
    sns.boxplot(data=df, x="species", y="body_mass_g", ax=axes[1])
    plt.tight_layout()
    plt.savefig("penguins.png", dpi=150)
    print("分析完成！圖表已存為 penguins.png")


if __name__ == "__main__":
    main()
