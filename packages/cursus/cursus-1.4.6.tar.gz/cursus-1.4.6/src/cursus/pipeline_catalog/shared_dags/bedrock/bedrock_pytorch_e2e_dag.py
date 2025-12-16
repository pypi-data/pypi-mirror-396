"""
Shared DAG definition for PyTorch End-to-End Pipeline with Bedrock Processing (Real-time)

This module provides the shared DAG definition for a complete PyTorch workflow
that incorporates Bedrock prompt template generation and real-time processing steps
for LLM-enhanced data processing before PyTorch training and calibration.

The DAG includes separate Bedrock real-time processing paths for training and calibration:

Training Flow:
1) Dummy Data Loading (training)
2) Tabular Preprocessing (training)
3) Bedrock Prompt Template Generation (shared)
4) Bedrock Processing (training) - receives data + templates (REAL-TIME)
5) PyTorch Model Training

Calibration Flow:
6) Dummy Data Loading (calibration)
7) Tabular Preprocessing (calibration)
8) Bedrock Processing (calibration) - receives data + templates (shared, REAL-TIME)
9) PyTorch Model Evaluation (calibration)

Final Steps:
10) Model Calibration
11) Package Model
12) Payload Generation
13) Model Registration

Key Features:
- Separate Bedrock real-time processing for training and calibration data
- Shared prompt template generation for consistency
- Real-time LLM-enhanced data processing using AWS Bedrock API
- Suitable for smaller datasets or latency-sensitive workflows
- Job type variants (training vs calibration) for different processing behaviors
- Complete end-to-end workflow from data loading to model registration
"""

import logging
from typing import Dict, Any

from ....api.dag.base_dag import PipelineDAG
from .. import DAGMetadata

logger = logging.getLogger(__name__)


def create_bedrock_pytorch_e2e_dag() -> PipelineDAG:
    """
    Create a DAG for Bedrock Real-time-enhanced PyTorch E2E pipeline.

    This DAG represents a complete end-to-end workflow that uses Bedrock
    prompt template generation and real-time processing to enhance data before
    PyTorch training, followed by calibration, packaging, registration,
    and evaluation. Provides real-time processing for latency-sensitive workflows.

    Returns:
        PipelineDAG: The directed acyclic graph for the pipeline
    """
    dag = PipelineDAG()

    # Add all nodes - incorporating Bedrock real-time processing steps with job type variants
    dag.add_node("DummyDataLoading_training")  # Dummy data load for training
    dag.add_node("TabularPreprocessing_training")  # Tabular preprocessing for training
    dag.add_node(
        "BedrockPromptTemplateGeneration"
    )  # Bedrock prompt template generation
    dag.add_node(
        "BedrockProcessing_training"
    )  # Bedrock real-time processing step for training
    dag.add_node("PyTorchTraining")  # PyTorch training step
    dag.add_node(
        "ModelCalibration_calibration"
    )  # Model calibration step with calibration variant
    dag.add_node("Package")  # Package step
    dag.add_node("Registration")  # MIMS registration step
    dag.add_node("Payload")  # Payload step
    dag.add_node("DummyDataLoading_calibration")  # Dummy data load for calibration
    dag.add_node(
        "TabularPreprocessing_calibration"
    )  # Tabular preprocessing for calibration
    dag.add_node(
        "BedrockProcessing_calibration"
    )  # Bedrock real-time processing step for calibration
    dag.add_node("PyTorchModelEval_calibration")  # Model evaluation step

    # Training flow with Bedrock real-time processing integration
    dag.add_edge("DummyDataLoading_training", "TabularPreprocessing_training")

    # Bedrock real-time processing flow for training - two inputs to BedrockProcessing_training
    dag.add_edge(
        "TabularPreprocessing_training", "BedrockProcessing_training"
    )  # Data input
    dag.add_edge(
        "BedrockPromptTemplateGeneration", "BedrockProcessing_training"
    )  # Template input

    # Enhanced data flows to PyTorch training
    dag.add_edge("BedrockProcessing_training", "PyTorchTraining")

    # Calibration flow with Bedrock real-time processing integration
    dag.add_edge("DummyDataLoading_calibration", "TabularPreprocessing_calibration")

    # Bedrock real-time processing flow for calibration - two inputs to BedrockProcessing_calibration
    dag.add_edge(
        "TabularPreprocessing_calibration", "BedrockProcessing_calibration"
    )  # Data input
    dag.add_edge(
        "BedrockPromptTemplateGeneration", "BedrockProcessing_calibration"
    )  # Template input

    # Evaluation flow
    dag.add_edge("PyTorchTraining", "PyTorchModelEval_calibration")
    dag.add_edge(
        "BedrockProcessing_calibration", "PyTorchModelEval_calibration"
    )  # Use Bedrock-processed calibration data

    # Model calibration flow - depends on model evaluation
    dag.add_edge("PyTorchModelEval_calibration", "ModelCalibration_calibration")

    # Output flow
    dag.add_edge("ModelCalibration_calibration", "Package")
    dag.add_edge("PyTorchTraining", "Package")  # Raw model is also input to packaging
    dag.add_edge("PyTorchTraining", "Payload")  # Payload test uses the raw model
    dag.add_edge("Package", "Registration")
    dag.add_edge("Payload", "Registration")

    logger.info(
        f"Created Bedrock Real-time-PyTorch E2E DAG with {len(dag.nodes)} nodes and {len(dag.edges)} edges"
    )
    return dag


def get_dag_metadata() -> DAGMetadata:
    """
    Get metadata for the Bedrock Real-time-enhanced PyTorch end-to-end DAG.

    Returns:
        DAGMetadata: Metadata describing the DAG structure and purpose
    """
    return DAGMetadata(
        description="Bedrock Real-time-enhanced PyTorch end-to-end pipeline with LLM-based data processing, training, calibration, packaging, registration, and evaluation",
        complexity="comprehensive",
        features=[
            "dummy_data_loading",
            "bedrock_prompt_generation",
            "bedrock_realtime_processing",
            "training",
            "calibration",
            "packaging",
            "registration",
            "evaluation",
        ],
        framework="pytorch",
        node_count=13,
        edge_count=15,
        extra_metadata={
            "name": "bedrock_pytorch_e2e",
            "task_type": "end_to_end_with_realtime_llm",
            "entry_points": [
                "DummyDataLoading_training",
                "DummyDataLoading_calibration",
                "BedrockPromptTemplateGeneration",
            ],
            "exit_points": ["Registration"],
            "required_configs": [
                "DummyDataLoading_training",
                "DummyDataLoading_calibration",
                "TabularPreprocessing_training",
                "TabularPreprocessing_calibration",
                "BedrockPromptTemplateGeneration",
                "BedrockProcessing_training",
                "BedrockProcessing_calibration",
                "PyTorchTraining",
                "PyTorchModelEval_calibration",
                "ModelCalibration_calibration",
                "Package",
                "Payload",
                "Registration",
            ],
            "bedrock_integration": {
                "template_generation": "BedrockPromptTemplateGeneration",
                "training_processing": "BedrockProcessing_training",
                "calibration_processing": "BedrockProcessing_calibration",
                "processing_mode": "real-time",
                "training_flow": {
                    "input_sources": [
                        "TabularPreprocessing_training",
                        "BedrockPromptTemplateGeneration",
                    ],
                    "output_target": "PyTorchTraining",
                },
                "calibration_flow": {
                    "input_sources": [
                        "TabularPreprocessing_calibration",
                        "BedrockPromptTemplateGeneration",
                    ],
                    "output_target": "PyTorchModelEval_calibration",
                },
            },
        },
    )
