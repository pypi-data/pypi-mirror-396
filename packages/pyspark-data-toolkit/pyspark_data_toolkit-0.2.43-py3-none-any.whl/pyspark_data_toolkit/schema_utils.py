from typing import List, Dict, Optional, Any
import re
import logging
from pyspark.sql import DataFrame, functions as F
from logging_metrics import configure_basic_logging
from pyspark.sql.types import IntegerType, DoubleType, StringType, BooleanType, StructType, FloatType, DecimalType, ShortType, TimestampType
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StringType, IntegerType, LongType, DoubleType, BooleanType, ArrayType

from pyspark.sql.types import StructType, StructField, ArrayType
from delta.tables import DeltaTable

__all__ = [
    "apply_schema",
    "cast_columns_types_by_schema",
    "validate_dataframe_schema",
    "cast_column_to_table_schema",
    "cast_multiple_columns_to_table_schema",
    "align_dataframe_to_table_schema",
    "get_table_schema_info",
    "align_dataframe_to_table_schema_sample"
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()


def apply_schema(df: DataFrame, schema: Dict[str, Any], log: Optional[logging.Logger] = None) -> DataFrame:
    """Applies a schema by selecting and casting columns.

    This function:
      1. Selects only columns defined in `schema["columns"]`.
      2. Casts column types as defined in schema.

    Args:
        df (DataFrame): Input Spark DataFrame.
        schema (Dict[str, Any]): Dictionary with "columns" key containing a list of:
            - "column_name": Name of the column.
            - "data_type": Target type (string, int, date, etc.).

    Returns:
        DataFrame: DataFrame with selected and casted columns.
    """
    logger = log or get_logger()
    logger.info("Applying schema to DataFrame.")

    columns = [col["column_name"] for col in schema["columns"]]
    df = df.select(*columns)

    return cast_columns_types_by_schema(
        df,
        schema_list=schema["columns"],
        empty_to_null=True,
        logger=logger
    )


def cast_columns_types_by_schema(
    df: DataFrame, 
    schema_list: List[Dict[str, str]], 
    empty_to_null: bool = False, 
    truncate_strings: bool = False, 
    max_string_length: int = 16382,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Converte colunas para os tipos especificados no schema.
    
    Args:
        df: DataFrame de entrada
        schema_list: Lista de dicionários com 'column_name' e 'data_type'
        empty_to_null: Converter strings vazias para null
        truncate_strings: Truncar strings longas
        max_string_length: Tamanho máximo para strings
        logger: Logger opcional
        
    Returns:
        DataFrame com colunas convertidas
    """
    if logger is None:
        logger = get_logger()
        
    if df is None or not schema_list:
        raise ValueError("DataFrame e schema não podem ser nulos ou vazios")
    
    result_df = df
    
    for column in schema_list:
        column_name = column['column_name']
        data_type = column['data_type'].lower()
        
        # Verifica se a coluna existe no DataFrame
        if column_name not in result_df.columns:
            logger.warning(f"Coluna {column_name} não encontrada no DataFrame. Pulando.")
            continue
            
        logger.debug(f"Convertendo coluna {column_name} para tipo {data_type}")
        
        try:
            # Integer
            if re.match(r'int(eger)?(?!.*big)', data_type):
                result_df = result_df.withColumn(column_name, F.col(column_name).cast(IntegerType()))
                
            # Boolean
            elif 'bool' in data_type or 'boolean' in data_type:
                result_df = result_df.withColumn(column_name, F.col(column_name).cast(BooleanType()))
                
            # Numeric/Float types
            elif any(t in data_type for t in ['numeric', 'decimal', 'double', 'float', 'real', 'money', 'currency']):
                result_df = result_df.withColumn(column_name, F.col(column_name).cast(DoubleType()))
                
            # Date
            elif data_type == 'date':
                result_df = result_df.withColumn(column_name, F.to_date(F.col(column_name)))
                
            # Timestamp/Datetime
            elif data_type == 'datetime' or 'timestamp' in data_type:
                # Tenta vários formatos comuns
                result_df = result_df.withColumn(
                    column_name, 
                    F.coalesce(
                        F.to_timestamp(F.col(column_name), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"),
                        F.to_timestamp(F.col(column_name), "yyyy-MM-dd HH:mm:ss.SSS"),
                        F.to_timestamp(F.col(column_name), "yyyy-MM-dd HH:mm:ss"),
                        F.to_timestamp(F.col(column_name))
                    )
                )
                
            # Complex types - skip
            elif data_type in ['struct', 'array', 'map']:
                logger.debug(f"Tipo complexo {data_type} para coluna {column_name}: mantendo como está")
                continue
                
            # String (default)
            else:
                result_df = result_df.withColumn(column_name, F.trim(F.col(column_name).cast(StringType())))
                
                # Limpa caracteres problemáticos
                result_df = result_df.withColumn(
                    column_name, 
                    F.regexp_replace(F.col(column_name), "[\\r\\n\\t]", ' ')
                )
                
            # Trunca strings longas se solicitado
            if truncate_strings:
                result_df = result_df.withColumn(
                column_name, 
                F.substring(F.col(column_name), 1, max_string_length)
            )
                    
            # Converte strings vazias para null
            if empty_to_null:
                result_df = result_df.withColumn(
                column_name, 
                F.when(F.trim(F.col(column_name)) == "", None).otherwise(F.col(column_name))
            )
        
        except Exception as e:
            logger.error(f"Erro ao converter coluna {column_name}: {str(e)}")
            # Continua com outras colunas em caso de erro
    
    return result_df


def validate_dataframe_schema(df: DataFrame, schema: Dict[str, Any]) -> bool:
    """Validates that all columns defined in the schema exist in the DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        schema (Dict[str, Any]): Dictionary with "columns" key and list of:
            - "column_name": Column to validate.

    Returns:
        bool: True if all schema columns exist in DataFrame, False otherwise.
    """
    expected_cols = {col["column_name"] for col in schema.get("columns", [])}
    actual_cols = set(df.columns)
    return expected_cols.issubset(actual_cols)

# spark_utils/schema_utils.py ou my_library/spark/schema.py

def cast_column_to_table_schema(
    df: DataFrame, 
    target_table: str, 
    column_name: str,
    spark: Optional[SparkSession] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Converte uma coluna para o tipo de dados definido no schema de uma tabela existente.
    
    Útil para compatibilizar schemas antes de operações como MERGE ou INSERT,
    especialmente quando há incompatibilidades de tipo entre DataFrames.
    
    Args:
        df: DataFrame de origem
        target_table: Nome da tabela de destino (formato: database.table ou table)
        column_name: Nome da coluna a ser convertida
        spark: SparkSession (opcional, tenta obter da sessão ativa se não fornecido)
        
    Returns:
        DataFrame com a coluna convertida para o tipo correto
        
    Raises:
        ValueError: Se a coluna não existir na tabela de destino
        RuntimeError: Se não conseguir acessar a tabela ou obter o SparkSession
        
    Examples:
        >>> # Converte coluna 'status' para o tipo definido na tabela 'users'
        >>> df_fixed = cast_column_to_table_schema(df, "users", "status")
        >>> 
        >>> # Com SparkSession explícito
        >>> df_fixed = cast_column_to_table_schema(df, "db.users", "created_at", spark)
    """
    if logger is None:
        logger = get_logger()

    if spark is None:
        try:
            spark = SparkSession.getActiveSession()
            if spark is None:
                raise RuntimeError("Não foi possível obter SparkSession ativa")
        except Exception as e:
            raise RuntimeError(f"Erro ao obter SparkSession: {e}")
    
    try:
        # Obtém o schema da tabela de destino
        target_schema = spark.table(target_table).schema
    except Exception as e:
        raise RuntimeError(f"Erro ao acessar tabela '{target_table}': {e}")
    
    # Encontra o tipo da coluna no schema de destino
    target_column_type = None
    for field in target_schema.fields:
        if field.name == column_name:
            target_column_type = field.dataType
            break
    
    if target_column_type is None:
        available_columns = [field.name for field in target_schema.fields]
        raise ValueError(
            f"Coluna '{column_name}' não encontrada na tabela '{target_table}'. "
            f"Colunas disponíveis: {available_columns}"
        )
    
    logger.info(f"Convertendo coluna '{column_name}' para tipo {target_column_type}")
    
    # Aplica o cast correto
    return df.withColumn(column_name, F.lit(None).cast(target_column_type))

def cast_multiple_columns_to_table_schema(
    df: DataFrame,
    target_table: str,
    column_names: List[str],
    spark: Optional[SparkSession] = None
) -> DataFrame:
    """
    Converte múltiplas colunas para os tipos definidos no schema de uma tabela.
    
    Args:
        df: DataFrame de origem
        target_table: Nome da tabela de destino
        column_names: Lista de nomes das colunas a serem convertidas
        spark: SparkSession (opcional)
        
    Returns:
        DataFrame com as colunas convertidas
        
    Examples:
        >>> columns_to_fix = ["status", "created_at", "user_id"]
        >>> df_fixed = cast_multiple_columns_to_table_schema(df, "users", columns_to_fix)
    """
    result_df = df
    for column_name in column_names:
        result_df = cast_column_to_table_schema(result_df, target_table, column_name, spark)
    return result_df

def get_table_schema_info(
    table_name: str,
    spark: Optional[SparkSession] = None
) -> Dict[str, str]:
    """
    Obtém informações do schema de uma tabela.
    
    Args:
        table_name: Nome da tabela
        spark: SparkSession (opcional)
        
    Returns:
        Dicionário com {column_name: data_type}
        
    Examples:
        >>> schema_info = get_table_schema_info("users")
        >>> print(schema_info)
        {'id': 'bigint', 'name': 'string', 'created_at': 'timestamp'}
    """
    if spark is None:
        spark = SparkSession.getActiveSession()
        if spark is None:
            raise RuntimeError("Não foi possível obter SparkSession ativa")
    
    try:
        schema = spark.table(table_name).schema
        return {field.name: str(field.dataType) for field in schema.fields}
    except Exception as e:
        raise RuntimeError(f"Erro ao obter schema da tabela '{table_name}': {e}")

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, ArrayType, StringType, LongType, BooleanType

def align_array_struct_column(df, col_name, target_type: ArrayType):
    """
    Alinha uma coluna array<struct> ao schema target, preenchendo campos faltantes com null.
    Funciona recursivamente para structs internos e arrays internos.
    """
    element_type = target_type.elementType
    target_fields = {f.name: f for f in element_type.fields}

    def build_struct_expr(element_col, target_fields):
        exprs = []
        for name, field in target_fields.items():
            if isinstance(field.dataType, StructType):
                # Struct interno
                inner_expr = build_struct_expr(F.col(f"{element_col}.{name}"), {f.name: f for f in field.dataType.fields})
                exprs.append(inner_expr.alias(name))
            elif isinstance(field.dataType, ArrayType) and isinstance(field.dataType.elementType, StructType):
                # Array de struct interno
                exprs.append(
                    F.transform(
                        F.col(f"{element_col}.{name}"),
                        lambda x: build_struct_expr(x, {f.name: f for f in field.dataType.elementType.fields})
                    ).alias(name)
                )
            else:
                # Campo simples
                exprs.append(
                    F.col(f"{element_col}.{name}").cast(field.dataType).alias(name)
                )
        return F.struct(*exprs)

    return df.withColumn(
        col_name,
        F.when(
            F.col(col_name).isNotNull(),
            F.transform(F.col(col_name), lambda x: build_struct_expr(x, target_fields))
        ).otherwise(F.lit(None))
    )

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, ArrayType, StringType, LongType, BooleanType

def align_array_struct_column(df, col_name, target_type: ArrayType):
    """
    Alinha uma coluna array<struct> ao schema target, preenchendo campos faltantes com null.
    Funciona recursivamente para structs internos e arrays internos.
    """
    element_type = target_type.elementType
    target_fields = {f.name: f for f in element_type.fields}

    def build_struct_expr(element_col, target_fields):
        exprs = []
        for name, field in target_fields.items():
            if isinstance(field.dataType, StructType):
                # Struct interno
                inner_expr = build_struct_expr(F.col(f"{element_col}.{name}"), {f.name: f for f in field.dataType.fields})
                exprs.append(inner_expr.alias(name))
            elif isinstance(field.dataType, ArrayType) and isinstance(field.dataType.elementType, StructType):
                # Array de struct interno
                exprs.append(
                    F.transform(
                        F.col(f"{element_col}.{name}"),
                        lambda x: build_struct_expr(x, {f.name: f for f in field.dataType.elementType.fields})
                    ).alias(name)
                )
            else:
                # Campo simples
                exprs.append(
                    F.col(f"{element_col}.{name}").cast(field.dataType).alias(name)
                )
        return F.struct(*exprs)

    return df.withColumn(
        col_name,
        F.when(
            F.col(col_name).isNotNull(),
            F.transform(F.col(col_name), lambda x: build_struct_expr(x, target_fields))
        ).otherwise(F.lit(None))
    )

def align_dataframe_to_table_schema(
    df_source: DataFrame,
    table_name: str,
    merge_columns: bool = True,
    spark: Optional[SparkSession] = None,
) -> tuple[DataFrame, StructType]:
    """
    Prepara um DataFrame para merge em uma tabela Delta, fazendo schema evolution automático.
    
    Args:
        spark: SparkSession
        df_source: DataFrame de origem (bronze)
        table_name: Nome da tabela (ex: 'hive_metastore.cms' ou 'catalog.schema.table')
        merge_columns: Se True, faz merge dos schemas (adiciona colunas novas do source)
    
    Returns:
        Tupla com (DataFrame alinhado, Schema final)
    """
    # from .schema_utils import build_safe_struct
    
    # 1. Obter schema da tabela Delta
    table_schema = get_table_schema(spark, table_name)
    
    # 2. Merge dos schemas (target + novos campos do source)
    if merge_columns:
        final_schema = merge_schemas(df_source.schema, table_schema)
    else:
        final_schema = table_schema
    
    # 3. Alinhar DataFrame ao schema final
    df_aligned = df_source
    
    for field in final_schema.fields:
        col_name = field.name
        
        if col_name not in df_aligned.columns:
            # Campo não existe no source - adicionar como NULL
            df_aligned = df_aligned.withColumn(col_name, F.lit(None).cast(field.dataType))
        else:
            # Campo existe - alinhar estrutura interna
            if isinstance(field.dataType, StructType):
                df_aligned = df_aligned.withColumn(
                    col_name,
                    build_safe_struct(col_name, field.dataType, df_source.schema)
                )
    
    # 4. Selecionar colunas na ordem do schema final
    df_aligned = df_aligned.select([field.name for field in final_schema.fields])
    
    return df_aligned, final_schema

def get_table_schema(spark, table_name: str) -> StructType:
    """
    Obtém o schema de uma tabela Delta existente.
    
    Args:
        spark: SparkSession
        table_name: Nome completo da tabela no formato catalog.schema.table
                   (ex: 'hive_metastore.cms.bandarticle')
    
    Returns:
        Schema da tabela
    """
    # Limpa e valida o nome da tabela
    table_name = table_name.strip()
    parts = [p.strip() for p in table_name.split('.')]
    parts = [p for p in parts if p]  # Remove partes vazias
    
    if len(parts) != 3:
        raise ValueError(
            f"O nome da tabela deve estar no formato 'catalog.schema.table'. "
            f"Recebido: '{table_name}' com {len(parts)} partes: {parts}"
        )
    
    catalog, schema, table = parts
    full_table_name = f"{catalog}.{schema}.{table}"
    
    try:
        # Método 1: Usando USE catalog + schema (mais confiável para 3-level namespace)
        spark.sql(f"USE CATALOG {catalog}")
        spark.sql(f"USE SCHEMA {schema}")
        df = spark.table(table)
        return df.schema
        
    except Exception as e1:
        try:
            # Método 2: Usando nome completo diretamente
            df = spark.table(full_table_name)
            return df.schema
            
        except Exception as e2:
            try:
                # Método 3: DeltaTable com nome completo
                delta_table = DeltaTable.forName(spark, full_table_name)
                return delta_table.toDF().schema
                
            except Exception as e3:
                try:
                    # Método 4: SQL SELECT com nome completo
                    df = spark.sql(f"SELECT * FROM {full_table_name} LIMIT 0")
                    return df.schema
                    
                except Exception as e4:
                    raise Exception(
                        f"Não foi possível obter schema da tabela '{table_name}'.\n"
                        f"Formato esperado: catalog.schema.table\n"
                        f"Partes detectadas: {parts}\n"
                        f"Nome completo: {full_table_name}\n"
                        f"Tentativas:\n"
                        f"  1. USE CATALOG + USE SCHEMA: {str(e1)[:150]}\n"
                        f"  2. spark.table(full_name): {str(e2)[:150]}\n"
                        f"  3. DeltaTable.forName: {str(e3)[:150]}\n"
                        f"  4. spark.sql(SELECT): {str(e4)[:150]}"
                    )

def merge_schemas(source_schema: StructType, target_schema: StructType) -> StructType:
    """
    Mescla dois schemas, pegando todos os campos do target e adicionando
    campos novos do source que não existem no target.
    """
    target_fields = {f.name: f for f in target_schema.fields}
    merged_fields = list(target_schema.fields)
    
    for source_field in source_schema.fields:
        if source_field.name not in target_fields:
            # Campo novo do source que não existe no target
            merged_fields.append(source_field)
        else:
            # Campo existe em ambos - fazer merge recursivo se for struct
            target_field = target_fields[source_field.name]
            
            if isinstance(source_field.dataType, StructType) and isinstance(target_field.dataType, StructType):
                # Merge recursivo de structs
                merged_struct = merge_schemas(source_field.dataType, target_field.dataType)
                idx = merged_fields.index(target_field)
                merged_fields[idx] = StructField(
                    source_field.name,
                    merged_struct,
                    nullable=source_field.nullable or target_field.nullable
                )
            elif isinstance(source_field.dataType, ArrayType) and isinstance(target_field.dataType, ArrayType):
                # Merge de arrays com structs
                if isinstance(source_field.dataType.elementType, StructType) and \
                   isinstance(target_field.dataType.elementType, StructType):
                    merged_struct = merge_schemas(
                        source_field.dataType.elementType,
                        target_field.dataType.elementType
                    )
                    idx = merged_fields.index(target_field)
                    merged_fields[idx] = StructField(
                        source_field.name,
                        ArrayType(merged_struct, containsNull=source_field.dataType.containsNull),
                        nullable=source_field.nullable or target_field.nullable
                    )
    
    return StructType(merged_fields)

def build_safe_struct(parent_col: str, target_schema: StructType, full_schema: StructType):
    """
    Constrói uma struct alinhada ao target_schema, tratando campos aninhados e arrays.
    
    IMPORTANTE: 
    - Garante que os campos estejam na ordem correta do target schema
    - Para arrays de structs, USA TRANSFORM em vez de CAST
    - Cast só funciona para tipos primitivos, não para reordenar structs
    
    Args:
        parent_col: Nome da coluna pai (ex: "config", "route.map")
        target_schema: Schema desejado (da tabela Delta)
        full_schema: Schema atual do DataFrame
        
    Returns:
        Expressão F.struct() com campos alinhados ao target
    """
    fields = []

    for field in target_schema.fields:
        field_name = field.name
        full_path = f"{parent_col}.{field_name}"

        if struct_has_field(full_schema, full_path):
            source_type = get_field_schema(full_schema, full_path)

            # Struct aninhado
            if isinstance(field.dataType, StructType):
                value = build_safe_struct(full_path, field.dataType, full_schema)

            # Array<Struct> - NUNCA usar cast, sempre transform
            elif isinstance(field.dataType, ArrayType) and isinstance(field.dataType.elementType, StructType):
                if source_type and isinstance(source_type, ArrayType) and isinstance(source_type.elementType, StructType):
                    # Usar transform para reordenar campos dentro do array
                    value = F.when(
                        F.col(full_path).isNotNull(),
                        F.transform(
                            F.col(full_path),
                            lambda x: build_safe_struct_from_array_struct(
                                x, 
                                field.dataType.elementType, 
                                source_type.elementType
                            )
                        )
                    ).otherwise(F.array())
                else:
                    # Source não é array<struct>, retorna array vazio
                    value = F.array()

            # Array de tipos simples - pode usar cast
            elif isinstance(field.dataType, ArrayType):
                value = F.col(full_path).cast(field.dataType)

            # Tipo simples
            else:
                value = F.col(full_path).cast(field.dataType)

        else:
            # Campo não existe no source
            value = F.lit(None).cast(field.dataType)

        fields.append(value.alias(field_name))

    return F.struct(*fields)

def struct_has_field(schema: StructType, path: str) -> bool:
    """Verifica se um campo existe no schema através de um path."""
    parts = path.split(".")
    current = schema

    for part in parts:
        if isinstance(current, StructType) and part in [f.name for f in current.fields]:
            field = [f for f in current.fields if f.name == part][0]
            current = field.dataType

            if isinstance(current, ArrayType):
                current = current.elementType

        else:
            return False

    return True

def get_field_schema(schema: StructType, path: str):
    """Obtém o schema de um campo através de um path."""
    parts = path.split(".")
    current = schema

    for part in parts:
        field = next((f for f in current.fields if f.name == part), None)

        if field is None:
            return None

        current = field.dataType

        if isinstance(current, ArrayType):
            current = current.elementType

    return current

def build_safe_struct_from_array_struct(col, target_schema: StructType, source_schema: StructType):
    """
    Constrói uma struct alinhada ao target_schema a partir de um elemento de array.
    Garante que os campos estejam na ordem correta do target schema.
    CRÍTICO: Não usa cast em arrays/structs, apenas em tipos primitivos.
    """
    if not isinstance(source_schema, StructType):
        # Se source não é struct, retorna None cast para target
        return F.lit(None).cast(target_schema)
    
    fields = []
    source_fields = {f.name: f for f in source_schema.fields}

    for target_field in target_schema.fields:
        field_name = target_field.name
        
        if field_name in source_fields:
            source_field = source_fields[field_name]
            
            # Struct aninhado
            if isinstance(target_field.dataType, StructType):
                if isinstance(source_field.dataType, StructType):
                    value = build_safe_struct_from_array_struct(
                        col.getField(field_name),
                        target_field.dataType,
                        source_field.dataType
                    )
                else:
                    value = F.lit(None).cast(target_field.dataType)
            
            # Array de structs aninhado
            elif isinstance(target_field.dataType, ArrayType) and isinstance(target_field.dataType.elementType, StructType):
                if isinstance(source_field.dataType, ArrayType) and isinstance(source_field.dataType.elementType, StructType):
                    # Transform recursivo para arrays aninhados
                    value = F.when(
                        col.getField(field_name).isNotNull(),
                        F.transform(
                            col.getField(field_name),
                            lambda nested_item: build_safe_struct_from_array_struct(
                                nested_item,
                                target_field.dataType.elementType,
                                source_field.dataType.elementType
                            )
                        )
                    ).otherwise(F.array())
                else:
                    value = F.array()
            
            # Tipo simples (String, Long, etc)
            else:
                value = col.getField(field_name).cast(target_field.dataType)
        else:
            # Campo não existe no source
            value = F.lit(None).cast(target_field.dataType)

        fields.append(value.alias(field_name))

    return F.struct(*fields)

# ----------------------------------------------
# def align_dataframe_to_table_schema(
#     df: DataFrame,
#     target_table: str,
#     cast_existing: bool = True,
#     add_missing: bool = True,
#     spark: Optional[SparkSession] = None,
#     logger: Optional[logging.Logger] = None
# ) -> DataFrame:
#     if logger is None:
#         logger = get_logger()

#     if spark is None:
#         spark = SparkSession.getActiveSession()
#         if spark is None:
#             raise RuntimeError("Não foi possível obter SparkSession ativa")
    
#     try:
#         target_schema = spark.table(target_table).schema
#     except Exception as e:
#         raise RuntimeError(f"Erro ao acessar tabela '{target_table}': {e}")
    
#     result_df = df
#     current_columns = set(df.columns)
#     target_columns = {field.name: field.dataType for field in target_schema.fields}
    
#     # Coleta tipos atuais ANTES de qualquer modificação (evita erros em dtypes)
#     original_dtypes = dict(df.dtypes)  # Usa df original, não result_df
    
#     # Adiciona colunas ausentes
#     if add_missing:
#         missing_columns = set(target_columns.keys()) - current_columns
#         for col_name in missing_columns:
#             col_type = target_columns[col_name]
#             default_value = _get_default_value_for_type(col_type)
#             result_df = result_df.withColumn(col_name, F.lit(default_value).cast(col_type))
#             logger.info(f"Adicionada coluna ausente '{col_name}' como {col_type}")
    
#     # Converte tipos das colunas existentes - usa original_dtypes para check
#     if cast_existing:
#         existing_columns = current_columns.intersection(target_columns.keys())
#         for col_name in existing_columns:
#             target_type = target_columns[col_name]
#             current_type = original_dtypes.get(col_name, str(df.schema[col_name].dataType))  # Seguro, do original
            
#             if str(target_type) != current_type:
#                 try:
#                     # Verifica se é conversão de array<struct>
#                     if _is_array_struct_conversion(current_type, target_type):
#                         result_df = _convert_array_struct_column(
#                             result_df, col_name, target_type, logger
#                         )
#                     else:
#                         from pyspark.sql.types import StructType
#                         if isinstance(target_type, StructType):
#                             if col_name in result_df.columns:
#                                 source_struct = df.schema[col_name].dataType
#                                 aligned_expr = _align_struct_fields(F.col(col_name), target_type, logger, source_struct)
#                             else:
#                                 aligned_expr = _align_struct_fields(F.lit(None).cast(target_type), target_type, logger)
#                             result_df = result_df.withColumn(col_name, aligned_expr)
#                         logger.info(f"Convertida coluna '{col_name}' de {current_type} para {target_type}")
                    
#                 except Exception as cast_error:
#                     logger.error(f"Erro ao converter coluna '{col_name}': {cast_error}")
#                     raise
    
#     # Reordena colunas para corresponder ao schema da tabela
#     target_column_order = [field.name for field in target_schema.fields if field.name in result_df.columns]
#     result_df = result_df.select(*target_column_order)
    
#     return result_df


# def _is_array_struct_conversion(current_type: str, target_type) -> bool:
#     """Verifica se é uma conversão de array<struct> para array<struct>"""
#     return (
#         "array<struct<" in current_type.lower() and 
#         str(target_type).startswith("ArrayType(StructType")
#     )


# from pyspark.sql.types import ArrayType, StructType

# def _convert_array_struct_column(df, col_name, target_type, logger=None):
#     """
#     Converte coluna array<struct> alinhando schemas de forma inteligente.
#     Compatível com nested e tipos simples.
#     """
#     import pyspark.sql.functions as F

#     if not isinstance(target_type, ArrayType) or not isinstance(target_type.elementType, StructType):
#         if logger:
#             logger.warning(
#                 f"Ignorando conversão da coluna '{col_name}': "
#                 f"esperado ArrayType(StructType), recebido {target_type}"
#             )
#         return df

#     # Obtém o tipo atual da coluna
#     try:
#         current_type = _get_nested_field_type(df.schema, col_name)
#     except Exception as e:
#         if logger:
#             logger.warning(f"Não foi possível resolver tipo da coluna '{col_name}': {e}")
#         return df  # Não quebra o job — apenas ignora a coluna

#     # Se não for array<struct>, não tenta converter
#     if not (isinstance(current_type, ArrayType) and isinstance(current_type.elementType, StructType)):
#         if logger:
#             logger.debug(f"Coluna '{col_name}' não é array<struct>, tipo atual: {current_type}")
#         return df

#     current_struct = current_type.elementType
#     target_struct = target_type.elementType

#     current_fields = {f.name: f for f in current_struct.fields}
#     target_fields = {f.name: f for f in target_struct.fields}

#     if _should_evolve_schema(current_fields, target_fields):
#         return _evolve_array_struct_schema(df, col_name, current_fields, target_fields, logger)
#     else:
#         return _trim_array_struct_schema(df, col_name, target_fields, logger)

# from pyspark.sql.types import StructType, ArrayType, DataType

# def _get_nested_field_type(schema: StructType, col_path: str) -> DataType:
#     """
#     Retorna o tipo de uma coluna, mesmo que seja aninhada (ex: 'a.b.c').
#     Tolera campos simples e arrays de structs.
#     """
#     parts = col_path.split(".")
#     current_type = schema

#     for part in parts:
#         if isinstance(current_type, StructType):
#             field = next((f for f in current_type.fields if f.name == part), None)
#             if not field:
#                 raise KeyError(f"Campo '{part}' não encontrado em {current_type.simpleString()}")
#             current_type = field.dataType

#         elif isinstance(current_type, ArrayType):
#             # Entra no elemento interno, se for struct
#             if isinstance(current_type.elementType, StructType):
#                 current_type = current_type.elementType
#             else:
#                 # É um array simples, não precisa navegar mais
#                 return current_type

#         else:
#             # Se já chegamos em um tipo simples, não há mais nada a percorrer
#             return current_type

#     return current_type

# def _should_evolve_schema(current_fields: dict, target_fields: dict) -> bool:
#     """
#     Decide se deve fazer schema evolution ou trimming.
#     Evolve quando o target tem mais campos que o current.
#     """
#     current_field_names = set(current_fields.keys())
#     target_field_names = set(target_fields.keys())
    
#     # Se target tem mais campos, é evolução
#     return len(target_field_names - current_field_names) > 0


# def _evolve_array_struct_schema(
#     df: DataFrame, 
#     col_name: str, 
#     current_fields: dict, 
#     target_fields: dict, 
#     logger: Optional[logging.Logger] = None
# ) -> DataFrame:
#     """
#     Evolui o schema adicionando campos ausentes com valores padrão apropriados.
#     """
#     from pyspark.sql.functions import col, transform, struct, lit
    
#     # Criar expressão de transformação usando SQL string (mais confiável)
#     df_temp = df
#     df_temp.createOrReplaceTempView(f"temp_table_{col_name}")
    
#     # Construir lista de campos para o struct
#     struct_fields = []
#     for field_name, field in target_fields.items():
#         if field_name in current_fields:
#             # Campo existe - manter valor original
#             struct_fields.append(f"x.{field_name}")
#         else:
#             # Campo novo - usar valor padrão baseado no tipo
#             default_value = _get_sql_default_value_for_type(field.dataType)
#             struct_fields.append(f"{default_value} as {field_name}")
    
#     struct_expr = ", ".join(struct_fields)
    
#     # Usar SQL para fazer a transformação
#     sql_query = f"""
#         SELECT *,
#                TRANSFORM({col_name}, x -> STRUCT({struct_expr})) as {col_name}_new
#         FROM temp_table_{col_name}
#     """
    
#     result_df = df.sparkSession.sql(sql_query)
#     result_df = result_df.drop(col_name).withColumnRenamed(f"{col_name}_new", col_name)
    
#     if logger:
#         added_fields = set(target_fields.keys()) - set(current_fields.keys())
#         logger.info(f"Schema evolution em '{col_name}': adicionados campos {added_fields}")
    
#     return result_df


# def _trim_array_struct_schema(
#     df: DataFrame, 
#     col_name: str, 
#     target_fields: dict, 
#     logger: Optional[logging.Logger] = None
# ) -> DataFrame:
#     """
#     Remove campos extras, mantendo apenas os do schema de destino.
#     """
#     # Usar SQL para fazer a transformação
#     df_temp = df
#     df_temp.createOrReplaceTempView(f"temp_trim_{col_name}")
    
#     # Construir lista de campos para manter
#     field_list = ", ".join([f"x.{field_name}" for field_name in target_fields.keys()])
    
#     sql_query = f"""
#         SELECT *,
#                TRANSFORM({col_name}, x -> STRUCT({field_list})) as {col_name}_new
#         FROM temp_trim_{col_name}
#     """
    
#     result_df = df.sparkSession.sql(sql_query)
#     result_df = result_df.drop(col_name).withColumnRenamed(f"{col_name}_new", col_name)
    
#     if logger:
#         logger.info(f"Schema trimming em '{col_name}': mantidos apenas campos {list(target_fields.keys())}")
    
#     return result_df


# def _get_default_value_for_type(data_type):
#     """Retorna um valor default literal compatível com o tipo Spark."""
#     if isinstance(data_type, StringType):
#         return F.lit(None).cast(StringType())
#     if isinstance(data_type, BooleanType):
#         return F.lit(False)
#     if isinstance(data_type, (IntegerType, LongType,DoubleType, FloatType, DecimalType, ShortType)):
#         return F.lit(0)
#     if isinstance(data_type, TimestampType):
#         return F.lit(None).cast(TimestampType())
#     if isinstance(data_type, StructType):
#         # Struct → cria struct com todos os campos default
#         fields = [
#             _get_default_value_for_type(f.dataType).alias(f.name)
#             for f in data_type.fields
#         ]
#         return F.struct(*fields)
#     if isinstance(data_type, ArrayType):
#         return F.array()
#     return F.lit(None)
    
# def _get_sql_default_value_for_type(data_type):
#     """
#     Retorna valores padrão como strings SQL.
#     """
    
    
#     if isinstance(data_type, StringType):
#         return "''"  # String vazia
#     elif isinstance(data_type, (IntegerType, LongType)):
#         return "0"
#     elif isinstance(data_type, DoubleType):
#         return "0.0"
#     elif isinstance(data_type, BooleanType):
#         return "false"
#     elif isinstance(data_type, ArrayType):
#         return "array()"  # Array vazio
#     else:
#         return "null"  # Só usa NULL quando não há alternativa

# def _build_aligned_struct(col_expr, target_type, logger=None, build_default=False):
#     """
#     Reconstrói struct genérico expressionalmente, com handling safe para nulls/VOID/recursão default.
#     Modo build_default=True pula getField e usa só defaults (evita VOID em lit(None) sub-structs).
#     Genérico para qualquer nested level/coluna; schema inferido sem extract errors.
#     """
#     from pyspark.sql.functions import lit, when, isnull, struct as F_struct
#     from pyspark.sql.types import StructType, StringType, LongType, BooleanType
    
#     if not isinstance(target_type, StructType):
#         # Cast simples se target primitivo (safe para nulls/VOID)
#         return col_expr.cast(target_type)
    
#     struct_fields = []
    
#     for field in target_type.fields:
#         field_name = field.name  # str garantido
#         target_field_type = field.dataType
        
#         if build_default:
#             # Modo default: pula extração, usa só default para cada field (sem getField em VOID)
#             existing_val = lit(None)  # Placeholder null, mas field_value será default
#             if logger:
#                 logger.debug(f"Build default para {field_name}: usando defaults tipados")
#         else:
#             # Modo normal: extração safe com isNotNull()
#             existing_val = when(col_expr.isNotNull(), col_expr.getField(field_name)).otherwise(lit(None))
#             if logger:
#                 logger.debug(f"Extração normal {field_name} em {col_expr}: safe handling")
        
#         # Default baseado no tipo (sempre tipado, lit(None) cast se necessário)
#         if isinstance(target_field_type, StringType):
#             default_val = lit("")
#         elif isinstance(target_field_type, LongType):
#             default_val = lit(0)
#         elif isinstance(target_field_type, BooleanType):
#             default_val = lit(False)
#         elif isinstance(target_field_type, StructType):
#             # Recursão para sub-struct: usa build_default=True para evitar VOID
#             default_val = _build_aligned_struct(lit(None), target_field_type, logger, build_default=True)
#         else:
#             default_val = lit(None).cast(target_field_type)
        
#         # When para escolher: existing se não null, senão default (expressional, safe para VOID)
#         field_value = when(isnull(existing_val), default_val).otherwise(existing_val)
        
#         if isinstance(target_field_type, StructType):
#             # Se o valor é VOID ou estamos em modo default, manter build_default=True
#             propagate_default = build_default or (str(field_value._jc.toString()).endswith("void()") if hasattr(field_value, "_jc") else False)
#             final_field = _build_aligned_struct(
#                 field_value, target_field_type, logger, build_default=propagate_default
#             ).alias(field_name)
#         else:
#             final_field = field_value.cast(target_field_type).alias(field_name)
        
#         struct_fields.append(final_field)
    
#     # Novo struct raiz (schema inferido full do target, sem VOID propagation)
#     return F_struct(*struct_fields)

# def _align_struct_fields(col_expr, target_struct, logger):
#     """
#     Garante que uma coluna struct tenha exatamente os mesmos campos
#     e tipos do schema de destino (target_struct).
#     """
#     from pyspark.sql import functions as F, types as T

#     aligned_fields = []

#     for field in target_struct.fields:
#         field_name = field.name
#         field_type = field.dataType

#         try:
#             # Usa F.col sem acessar o JVM (_jc)
#             sub_col = col_expr.getField(field_name)
#             if isinstance(field_type, T.StructType):
#                 aligned_field = _align_struct_fields(sub_col, field_type, logger)
#             else:
#                 aligned_field = sub_col.cast(field_type)
#         except Exception:
#             # Campo ausente ou struct incompleta → cria campo default compatível
#             aligned_field = _get_default_value_for_type(field_type)
#             logger.debug(f"Campo '{field_name}' ausente — preenchido com default ({field_type.simpleString()})")

#         aligned_fields.append(aligned_field.alias(field_name))

#     return F.struct(*aligned_fields)

# def _align_struct_fields(col_expr, target_struct, logger, source_struct=None):
#     """
#     Alinha um struct de acordo com o schema de destino,
#     somente acessando campos existentes no schema de origem.
#     """
#     from pyspark.sql import functions as F, types as T

#     aligned_fields = []

#     # Campos existentes no schema de origem
#     source_fields = set()
#     if isinstance(source_struct, T.StructType):
#         source_fields = {f.name for f in source_struct.fields}

#     for field in target_struct.fields:
#         field_name = field.name
#         field_type = field.dataType

#         if field_name in source_fields:
#             sub_col = col_expr.getField(field_name)

#             if isinstance(field_type, T.StructType):
#                 # Recursivo
#                 aligned_field = _align_struct_fields(
#                     sub_col,
#                     field_type,
#                     logger,
#                     source_struct=dict((f.name, f.dataType) for f in source_struct.fields)[field_name]
#                     if isinstance(source_struct, T.StructType)
#                     else None
#                 )
#             else:
#                 aligned_field = sub_col.cast(field_type)

#             logger.debug(f"Campo '{field_name}' existe — aplicando cast")

#         else:
#             aligned_field = _get_default_value_for_type(field_type)
#             logger.debug(
#                 f"Campo '{field_name}' ausente — preenchido com default ({field_type.simpleString()})"
#             )

#         aligned_fields.append(aligned_field.alias(field_name))

#     return F.struct(*aligned_fields)

# def _align_struct_fields(col_expr, target_struct, logger):
#     """
#     Alinha uma struct ou array<struct> ao schema de destino.
#     Garante ordem, cria campos ausentes e trata nested e arrays.
#     """
#     from pyspark.sql import functions as F, types as T
#     from pyspark.sql.column import Column

#     # CASO 1 — Array de Struct
#     if isinstance(target_struct, T.ArrayType) and isinstance(target_struct.elementType, T.StructType):
#         logger.debug("Aplicando alinhamento em ARRAY<STRUCT>")
#         return F.transform(
#             col_expr,
#             lambda x: _align_struct_fields(x, target_struct.elementType, logger)
#         )

#     # CASO 2 — Struct normal
#     if isinstance(target_struct, T.StructType):
#         aligned_fields = []

#         for field in target_struct.fields:
#             field_name = field.name
#             field_type = field.dataType

#             try:
#                 sub_col = col_expr.getField(field_name)

#                 if isinstance(field_type, T.StructType) or (
#                     isinstance(field_type, T.ArrayType) and isinstance(field_type.elementType, T.StructType)
#                 ):
#                     aligned_field = _align_struct_fields(sub_col, field_type, logger)
#                 else:
#                     aligned_field = sub_col.cast(field_type)

#             except Exception:
#                 # Campo ausente → cria default
#                 aligned_field = _get_default_value_for_type(field_type)
#                 logger.debug(f"Campo '{field_name}' ausente — default aplicado ({field_type.simpleString()})")

#             aligned_fields.append(aligned_field.alias(field_name))

#         return F.struct(*aligned_fields)

#     # CASO 3 — Tipo primitivo
#     return col_expr.cast(target_struct)








    

