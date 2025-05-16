from pathlib import Path

import pandas as pd


def is_eres_safe_to_delete(row):
    if (
        row["dupControlNo"] == True
        and row["matType"] == "w  "
        and (row["loc"] == "ia   " or row["loc"] == "iarch")
        and pd.isna(row["itemNo"])
        and pd.isna(row["orderNo"])
        and pd.isna(row["holdingNo"])
    ):
        return True
    else:
        return False


def is_eres_for_review(row):
    if row["dupControlNo"] == False and (
        row["matType"] != "w  "
        or pd.notna(row["itemNo"])
        or pd.notna(row["orderNo"])
        or pd.notna(row["holdingNo"])
    ):
        return True
    else:
        return False


def get_eres_df() -> pd.DataFrame:
    df = pd.read_csv(
        "files/GovDocs-SierraExport.txt",
        header=0,
        quotechar='"',
        sep="^",
        names=[
            "bibNo",
            "matType",
            "loc",
            "controlNo",
            "itemNo",
            "orderNo",
            "holdingNo",
        ],
    )
    df["dupControlNo"] = df["controlNo"].duplicated(keep="last")
    df["safe2delete"] = df.apply(is_eres_safe_to_delete, axis=1)
    df["review"] = df.apply(is_eres_for_review, axis=1)

    return df


def produce_safe2delete_dups_report(df: pd.DataFrame) -> None:
    safe = df[df["safe2delete"] == True]
    safe.to_csv(
        "files/safe2delete-dups.csv", index=False, header=False, columns=["bibNo"]
    )


def produce_unsafe2delete_dups_report(df: pd.DataFrame) -> None:
    """Prefix bib control number in 001 with 'tmp'"""
    unsafe = df[(df["dupControlNo"] == True) & (df["safe2delete"] == False)]
    unsafe.to_csv(
        "files/unsafe2delete-dups.csv",
        index=False,
        header=False,
        columns=["bibNo", "matType", "loc", "controlNo"],
    )


def produce_overwrite_review_needed_report(df: pd.DataFrame) -> None:
    """For manual review post load"""
    review = df[df["review"] == True]
    review.to_csv(
        "files/unsafe2overwrite.csv",
        index=False,
        header=False,
        columns=[
            "bibNo",
            "matType",
            "loc",
            "controlNo",
            "itemNo",
            "orderNo",
            "holdingNo",
        ],
    )
