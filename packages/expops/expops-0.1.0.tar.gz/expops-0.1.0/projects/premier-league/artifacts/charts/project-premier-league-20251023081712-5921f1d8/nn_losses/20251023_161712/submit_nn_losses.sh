#!/bin/bash
#SBATCH --job-name=nn_losses
#SBATCH --output=/home/e/e0958526/mlops-platform/projects/premier-league/artifacts/charts/project-premier-league-20251023081712-5921f1d8/nn_losses/20251023_161712/slurm-%j.out
#SBATCH --error=/home/e/e0958526/mlops-platform/projects/premier-league/artifacts/charts/project-premier-league-20251023081712-5921f1d8/nn_losses/20251023_161712/slurm-%j.err
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

# Export environment variables
export MLOPS_PROJECT_ID=premier-league
export MLOPS_OUTPUT_DIR=/home/e/e0958526/mlops-platform/projects/premier-league/artifacts/charts/project-premier-league-20251023081712-5921f1d8/nn_losses/20251023_161712
export MLOPS_CHART_NAME=nn_losses
export MLOPS_RUN_ID=project-premier-league-20251023081712-5921f1d8
export MLOPS_CHART_TYPE=dynamic
export MLOPS_CHART_IMPORT_FILES=projects/premier-league/charts/plot_metrics.py
export MLOPS_GCP_PROJECT=mlops-platform-470017
export GOOGLE_APPLICATION_CREDENTIALS=projects/premier-league/keys/firestore.json
export MLOPS_PROBE_PATHS="{\"nn_a\": \"nn_training_a/train_and_evaluate_nn_classifier\", \"nn_b\": \"nn_training_b/train_and_evaluate_nn_classifier\"}"
export PYTHONPATH=/home/e/e0958526/mlops-platform/src:$PYTHONPATH

# Run the chart
/home/e/e0958526/mlops-platform/.venvs/premier-league-env-reporting/bin/python -u -m mlops.reporting.entrypoint 
