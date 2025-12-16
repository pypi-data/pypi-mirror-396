from profiles_rudderstack.material import WhtMaterial


def standardize_ref_name(warehouse_type: str, ref_name: str):
    """DEPRECATED for production code - applies warehouse-specific case normalization.

    This is the "wrong" way to get table names because it only handles case conversion,
    not path-to-name translation or other database naming rules.

    Production code MUST use WhtMaterial.string() instead, which calls the proper
    Go-side Material.String() / RFM.String() logic.

    This function is kept ONLY for integration test utilities that need to validate
    warehouse state without access to WhtMaterial objects.

    Args:
        warehouse_type: The warehouse type (e.g., "snowflake", "redshift")
        ref_name: The reference name to normalize

    Returns:
        Case-normalized name based on warehouse type
    """
    if warehouse_type == "snowflake":
        return ref_name.upper()
    if warehouse_type == "redshift":
        return ref_name.lower()
    return ref_name


def run_query(wh_client, query: str):
    try:
        result = wh_client.query_sql_with_result(query)
    except Exception as e:
        raise Exception(
            f"""Unable to run the following query: {query}\n with error: {e}"""
        )
    if result is None or result.empty:
        return result
    result.columns = result.columns.str.upper()
    return result
