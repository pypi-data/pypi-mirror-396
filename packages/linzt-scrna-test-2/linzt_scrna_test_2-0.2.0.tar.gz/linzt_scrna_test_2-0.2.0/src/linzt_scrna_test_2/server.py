from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class scrna_mcp_tools(str, Enum):
    run_cell_quality_control = 'run_cell_quality_control'
    run_doublet_filter = 'run_doublet_filter'
    run_normalization = 'run_normalization'
    run_data_integration = 'run_data_integration'
    run_find_hvg = 'run_find_hvg'
    run_data_reduction = 'run_data_reduction'
    run_cell_cluster = 'run_cell_cluster'
    run_find_marker = 'run_find_marker'
    run_cell_annotation = 'run_cell_annotation'
    run_deg = 'run_deg'
    run_trajectory = 'run_trajectory'
    run_cellchat = 'run_cellchat'
    run_transcription_factor_activity = 'run_transcription_factor_activity'
    run_go_enrichment = 'run_go_enrichment'
    run_kegg_enrichment = 'run_kegg_enrichment'


class run_cell_quality_control_inputs(BaseModel):
    seurat_obj: Any = Field(description = '质量控制前的 Seurat 对象文件路径（.rds 格式，需包含原始计数矩阵）')
    nFeature_RNA: Any = Field(description = '基因数量 **小于** 该值的细胞将被丢弃（*建议根据数据分布调整；新鲜组织通常 200-500，冷冻样本可降至 100-200*）')
    nCount_RNA: Any = Field(description = 'UMI 数量 **小于** 该值的细胞将被丢弃（*建议根据数据分布调整；高深度测序可设为 500-2000*）')
    mt_percent: Any = Field(description = '线粒体基因占比 **超过** 该值的细胞将被丢弃')
    hb_percent: Any = Field(description = '红细胞基因占比 **超过** 该值的细胞将被丢弃（*仅适用于血液/骨髓样本；非血液样本建议设为 `None`*）')

class run_cell_quality_control_outputs(BaseModel):
    seurat_obj: Any = Field(description = '质量控制后的 Seurat 对象文件路径（.rds 格式）')

def run_cell_quality_control(
        seurat_obj: Any,
        nFeature_RNA: Any = 200,
        nCount_RNA: Any = 800,
        mt_percent: Any = 15,
        hb_percent: Any = 0.1
    ) -> run_cell_quality_control_outputs:
    return run_cell_quality_control_outputs(
        seurat_obj = f'/output_datas/qc_seurat.rds'
    )


class run_doublet_filter_inputs(BaseModel):
    seurat_obj: Any = Field(description = '质量控制之后的 Seurat 对象文件路径（.rds 格式）')
    method: Any = Field(description = '双细胞检测方法')
    expected_doublet_rate: Any = Field(description = '预期双细胞率，通常为总细胞数的 5-10%。与细胞加载浓度正相关，高浓度样本可设为 0.08-0.10')
    pN: Any = Field(description = '人工双细胞占真实细胞的比例，通常无需调整')
    pK: Any = Field(description = '最近邻比例，默认 None 表示自动计算，也可手动指定如 "0.005"、"0.01" 等，通常自动计算即可')

class run_doublet_filter_outputs(BaseModel):
    seurat_obj: Any = Field(description = '双细胞过滤后的 Seurat 对象文件路径（.rds 格式）')

def run_doublet_filter(
        seurat_obj: Any,
        method: Any = "DoubletFinder",
        expected_doublet_rate: Any = 0.05,
        pN: Any = 0.25,
        pK: Any = None
    ) -> run_doublet_filter_outputs:
    return run_doublet_filter_outputs(
        seurat_obj = f'/output_datas/doublet_filtered_seurat.rds'
    )


class run_normalization_inputs(BaseModel):
    seurat_obj: Any = Field(description = '质控后（或双细胞过滤后）的 Seurat 对象文件路径（.rds 格式）')
    method: Any = Field(description = '标准化方法')
    scale_factor: Any = Field(description = '仅用于 "LogNormalize" 方法。将每个细胞的总 UMI 数缩放至该值，然后进行 log(1+x) 转换')
    variable_features_n: Any = Field(description = '仅用于 "SCTransform" 方法。指定保留的高可变基因数量，通常2000-5000')

class run_normalization_outputs(BaseModel):
    seurat_obj: Any = Field(description = '标准化后的 Seurat 对象文件路径（.rds 格式）')

def run_normalization(
        seurat_obj: Any,
        method: Any = "LogNormalize",
        scale_factor: Any = 10000,
        variable_features_n: Any = 2000
    ) -> run_normalization_outputs:
    return run_normalization_outputs(
        seurat_obj = f'/output_datas/normalized_seurat.rds'
    )


class run_data_integration_inputs(BaseModel):
    seurat_obj_list: Any = Field(description = '待整合的 Seurat 对象文件路径列表（.rds 格式文件路径列表）')
    method: Any = Field(description = '整合方法')
    nfeatures: Any = Field(description = '用于整合的特征（基因）数量')
    npcs: Any = Field(description = '用于整合的 PCA 维度数')

class run_data_integration_outputs(BaseModel):
    seurat_obj: Any = Field(description = '整合后的 Seurat 对象文件路径（.rds格式）')

def run_data_integration(
        seurat_obj_list: Any,
        method: Any = "harmony",
        nfeatures: Any = 2000,
        npcs: Any = 30
    ) -> run_data_integration_outputs:
    return run_data_integration_outputs(
        seurat_obj = f'/output_datas/integrated_seurat.rds'
    )


class run_find_hvg_inputs(BaseModel):
    seurat_obj: Any = Field(description = '标准化或数据整合后的 Seurat 对象文件路径（.rds 格式）')
    nfeatures: Any = Field(description = '选择的高可变基因数量。通常 2000-5000，大型数据集可增至 8000')
    selection_method: Any = Field(description = '筛选方法')

class run_find_hvg_outputs(BaseModel):
    seurat_obj: Any = Field(description = '包含高可变基因标记的 Seurat 对象文件路径（.rds 格式）')

def run_find_hvg(
        seurat_obj: Any,
        nfeatures: Any = 2000,
        selection_method: Any = "vst"
    ) -> run_find_hvg_outputs:
    return run_find_hvg_outputs(
        seurat_obj = f'/output_datas/hvg_seurat.rds'
    )


class run_data_reduction_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含高可变基因的 Seurat 对象文件路径（.rds 格式）')
    npcs: Any = Field(description = 'PCA 计算的主成分数量。通常 30-50，足够捕获主要变异')
    dimensions: Any = Field(description = '用于后续分析（如聚类、UMAP）的 PCA 维度数。通常 10-30，应基于 PCA 肘部图确定')

class run_data_reduction_outputs(BaseModel):
    seurat_obj: Any = Field(description = '包含降维结果的 Seurat 对象文件路径（.rds 格式）')

def run_data_reduction(
        seurat_obj: Any,
        npcs: Any = 50,
        dimensions: Any = 30
    ) -> run_data_reduction_outputs:
    return run_data_reduction_outputs(
        seurat_obj = f'/output_datas/reduced_seurat.rds'
    )


class run_cell_cluster_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含降维结果的 Seurat 对象文件路径（.rds 格式）')
    methods: Any = Field(description = '聚类算法')
    resolution: Any = Field(description = '聚类分辨率参数，控制簇的粒度。值越大，簇越多越细')

class run_cell_cluster_outputs(BaseModel):
    seurat_obj: Any = Field(description = '包含聚类标签的 Seurat 对象文件路径（.rds 格式）')

def run_cell_cluster(
        seurat_obj: Any,
        methods: Any = "louvain",
        resolution: Any = 0.8
    ) -> run_cell_cluster_outputs:
    return run_cell_cluster_outputs(
        seurat_obj = f'/output_datas/clustered_seurat.rds'
    )


class run_find_marker_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含聚类标签的 Seurat 对象文件路径（.rds 格式）')
    min_pct: Any = Field(description = '基因在簇中的最小表达比例。要求基因至少在 `min_pct` 比例的簇内细胞中表达')
    logfc_threshold: Any = Field(description = '对数倍数变化阈值。要求基因的平均表达差异至少达到该值（以 log2 scale 计）')
    threshold: Any = Field(description = '调整后p值（FDR）阈值。仅返回 FDR 小于此值的基因')

class run_find_marker_outputs(BaseModel):
    seurat_obj: Any = Field(description = '包含标记基因分析结果的 Seurat 对象文件路径（.rds 格式）')
    marker_result_file: Any = Field(description = '标记基因结果文件（.csv 格式），每个簇的 top 标记基因列表')

def run_find_marker(
        seurat_obj: Any,
        min_pct: Any = 0.25,
        logfc_threshold: Any = 0.25,
        threshold: Any = 0.05
    ) -> run_find_marker_outputs:
    return run_find_marker_outputs(
        seurat_obj = f'/output_datas/marker_seurat.rds',
        marker_result_file = f'/output_datas/marker_result.csv'
    )


class run_cell_annotation_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含标记基因分析结果的 Seurat 对象文件路径（.rds 格式）')
    min_score: Any = Field(description = '自动注释的最小置信度分数（0-1之间）。仅保留置信度高于此值的注释')

class run_cell_annotation_outputs(BaseModel):
    seurat_obj: Any = Field(description = '包含细胞类型注释的 Seurat 对象文件路径（.rds 格式）')
    cell_anno_file: Any = Field(description = '细胞类型注释结果文件（.csv 格式）')

def run_cell_annotation(
        seurat_obj: Any,
        min_score: Any = 0.5
    ) -> run_cell_annotation_outputs:
    return run_cell_annotation_outputs(
        seurat_obj = f'/output_datas/annotated_seurat.rds',
        cell_anno_file = f'/output_datas/cell_anno.csv'
    )


class run_deg_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含细胞类型注释的 Seurat 对象文件路径（.rds 格式）')
    logfc_threshold: Any = Field(description = '对数倍数变化阈值')
    threshold: Any = Field(description = '调整后 p 值阈值')

class run_deg_outputs(BaseModel):
    deg_result_file: Any = Field(description = '差异表达分析结果文件（.csv 格式）')

def run_deg(
        seurat_obj: Any,
        logfc_threshold: Any = 0.25,
        threshold: Any = 0.05
    ) -> run_deg_outputs:
    return run_deg_outputs(
        deg_result_file = f'/output_datas/deg_result.csv'
    )


class run_trajectory_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含细胞类型注释的 Seurat 对象文件路径（.rds 格式）')
    method: Any = Field(description = '轨迹推断方法')

class run_trajectory_outputs(BaseModel):
    seurat_obj: Any = Field(description = '包含轨迹信息的 Seurat/Monocle 对象文件路径（.rds 格式）')
    pseudotime_result_file: Any = Field(description = '轨迹结果文件（.csv 格式）')

def run_trajectory(
        seurat_obj: Any,
        method: Any = "monocle3"
    ) -> run_trajectory_outputs:
    return run_trajectory_outputs(
        seurat_obj = f'/output_datas/trajectory_seurat.rds',
        pseudotime_result_file = f'/output_datas/pseudotime_result.csv'
    )


class run_cellchat_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含细胞类型注释的 Seurat 对象文件路径（.rds 格式）')
    min_cells_per_group: Any = Field(description = '每组（细胞类型）最少细胞数。少于该数的组将被排除')
    prob_threshold: Any = Field(description = '相互作用概率阈值。仅保留概率高于此值的相互作用')
    
class run_cellchat_outputs(BaseModel):
    seurat_obj: Any = Field(description = 'CellChat 对象文件路径（.rds 格式），包含完整的细胞通讯分析结果')
    cell_chat_file: Any = Field(description = '细胞通讯网络结果文件（.csv 格式）')

def run_cellchat(
        seurat_obj: Any,
        min_cells_per_group: Any = 10,
        prob_threshold: Any = 0.05
    ) -> run_cellchat_outputs:
    return run_cellchat_outputs(
        seurat_obj = f'/output_datas/cellchat_seurat.rds',
        cell_chat_file = f'/output_datas/cellchat_result.csv'
    )


class run_transcription_factor_activity_inputs(BaseModel):
    seurat_obj: Any = Field(description = '包含细胞类型注释的 Seurat 对象文件路径（.rds 格式）')
    minsize: Any = Field(description = '每个 TF 的最小靶基因数。靶基因数少于此值的 TF 将被排除')
    nes_threshold: Any = Field(description = '富集分数阈值。仅保留 NES（标准化富集分数）绝对值高于此值的 TF')

class run_transcription_factor_activity_outputs(BaseModel):
    seurat_obj: Any = Field(description = '包含 TF 活性分数的 Seurat 对象文件路径（.rds 格式）')
    tf_activity_file: Any = Field(description = 'TF 活性结果文件（.csv 格式）')

def run_transcription_factor_activity(
        seurat_obj: Any,
        minsize: Any = 5,
        nes_threshold: Any = 0
    ) -> run_transcription_factor_activity_outputs:
    return run_transcription_factor_activity_outputs(
        seurat_obj = f'/output_datas/tf_activity_seurat.rds',
        tf_activity_file = f'/output_datas/tf_activity_result.csv'
    )


class run_go_enrichment_inputs(BaseModel):
    gene_list: Any = Field(description = '输入基因列表文件路径（如差异表达基因）')
    organism: Any = Field(description = '物种')
    pvalue_cutoff: Any = Field(description = 'p 值阈值（未校正）')
    qvalue_cutoff: Any = Field(description = 'q 值阈值（FDR 校正后）')

class run_go_enrichment_outputs(BaseModel):
    go_result_file: Any = Field(description = 'GO 富集分析结果文件（.csv 格式）')

def run_go_enrichment(
        gene_list: Any,
        organism: Any = "human",
        pvalue_cutoff: Any = 0.05,
        qvalue_cutoff: Any = 0.05
    ) -> run_go_enrichment_outputs:
    return run_go_enrichment_outputs(
        go_result_file = f'/output_datas/go_result.csv'
    )


class run_kegg_enrichment_inputs(BaseModel):
    gene_list: Any = Field(description = '输入基因列表文件路径（如差异表达基因）')
    organism: Any = Field(description = '物种')
    pvalue_cutoff: Any = Field(description = 'p 值阈值（未校正）')
    qvalue_cutoff: Any = Field(description = 'q 值阈值（FDR 校正后）')

class run_kegg_enrichment_outputs(BaseModel):
    kegg_result_file: Any = Field(description = 'KEGG 富集分析结果文件（.csv 格式）')

def run_kegg_enrichment(
        gene_list: Any,
        organism: Any = "human",
        pvalue_cutoff: Any = 0.05,
        qvalue_cutoff: Any = 0.05
    ) -> run_kegg_enrichment_outputs:
    return run_kegg_enrichment_outputs(
        kegg_result_file = f'/output_datas/kegg_result.csv'
    )


async def mcp_server() -> None:
    server = Server("scRNA MCP server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=scrna_mcp_tools.run_cell_quality_control,
                description=""" 细胞质量控制 """,
                inputSchema=run_cell_quality_control_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_doublet_filter,
                description=""" 多重细胞过滤 """,
                inputSchema=run_doublet_filter_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_normalization,
                description=""" 数据标准化 """,
                inputSchema=run_normalization_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_data_integration,
                description=""" 多样本/多批次数据整合 """,
                inputSchema=run_data_integration_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_find_hvg,
                description=""" 高可变基因筛选 """,
                inputSchema=run_find_hvg_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_data_reduction,
                description=""" 数据降维 """,
                inputSchema=run_data_reduction_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_cell_cluster,
                description=""" 细胞聚类分析 """,
                inputSchema=run_cell_cluster_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_find_marker,
                description=""" marker 基因筛选 """,
                inputSchema=run_find_marker_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_cell_annotation,
                description=""" 细胞注释 """,
                inputSchema=run_cell_annotation_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_deg,
                description=""" 差异表达分析 """,
                inputSchema=run_deg_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_trajectory,
                description=""" 拟时序分析 """,
                inputSchema=run_trajectory_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_cellchat,
                description=""" 细胞通讯分析 """,
                inputSchema=run_cellchat_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_transcription_factor_activity,
                description=""" 转录因子活性分析 """,
                inputSchema=run_transcription_factor_activity_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_go_enrichment,
                description=""" GO 富集分析 """,
                inputSchema=run_go_enrichment_inputs.model_json_schema(),
            ),
            Tool(
                name=scrna_mcp_tools.run_kegg_enrichment,
                description=""" KEGG 富集分析 """,
                inputSchema=run_kegg_enrichment_inputs.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        match name:
            case scrna_mcp_tools.run_cell_quality_control:
                return run_cell_quality_control(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_doublet_filter:
                return run_doublet_filter(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_normalization:
                return run_normalization(
                    seurat_obj = str(arguments["seurat_obj"])
                )
            
            case scrna_mcp_tools.run_data_integration:
                return run_data_integration(
                    seurat_obj_list = arguments["seurat_obj_list"]
                )

            case scrna_mcp_tools.run_find_hvg:
                return run_find_hvg(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_data_reduction:
                return run_data_reduction(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_cell_cluster:
                return run_cell_cluster(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_find_marker:
                return run_find_marker(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_cell_annotation:
                return run_cell_annotation(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_deg:
                return run_deg(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_trajectory:
                return run_trajectory(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_cellchat:
                return run_cellchat(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_transcription_factor_activity:
                return run_transcription_factor_activity(
                    seurat_obj = str(arguments["seurat_obj"])
                )

            case scrna_mcp_tools.run_go_enrichment:
                return run_go_enrichment(
                    gene_list = str(arguments["gene_list"])
                )

            case scrna_mcp_tools.run_kegg_enrichment:
                return run_kegg_enrichment(
                    gene_list = str(arguments["gene_list"])
                )
            
            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
