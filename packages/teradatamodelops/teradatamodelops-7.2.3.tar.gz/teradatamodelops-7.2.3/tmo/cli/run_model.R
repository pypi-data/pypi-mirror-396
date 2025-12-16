#!/usr/bin/env Rscript

library("jsonlite")
library("argparse")


parser <- ArgumentParser()

parser$add_argument("model_id",  help="The modelId to run")
parser$add_argument("project_id",  help="The projectId of the model")
parser$add_argument("mode", help="The mode (train or evaluate)")
parser$add_argument("data_path", help="Json file containing data configuration")
parser$add_argument("model_dir", help="Model Path")
args <- parser$parse_args()

model_id <- args$model_id
project_id <- args$project_id
mode <- tolower(args$mode)
model_dir <- args$model_dir

# get the configuration of the model
model_conf_dir <- paste0(model_dir, "/config.json")
model_conf <- jsonlite::read_json(model_conf_dir)

# get the json file to get the data
data_conf <- read_json(args$data_path)


# define the path of model modules
scripts_path <- paste0(model_dir, "/model_modules/")
training_path <- paste0(scripts_path, "training.R")
evaluation_path <- paste0(scripts_path, "evaluation.R")
scoring_path <- paste0(scripts_path, "scoring.R")


if (mode == "train") {
    source(training_path)
    train(
          data_conf=data_conf,
          model_conf=model_conf,
          model_id=model_id,
          model_version="cli",
          project_id=project_id,
          job_id=uuid::UUIDgenerate())
} else if (mode == "evaluate") {
    if (file.exists(evaluation_path)) {
        source(evaluation_path)
    }
    else {
        message("No evaluation.R found. Using scoring.R -> evaluate")
        source(scoring_path)
    }

    evaluate(
             data_conf=data_conf,
             model_conf=model_conf,
             model_id=model_id,
             model_version="cli",
             project_id=project_id,
             job_id=uuid::UUIDgenerate())
} else if (mode == "score.batch") {
    source(scoring_path)
    score.batch(data_conf, model_conf,
                model_id=model_id,
                model_version="cli",
                project_id=project_id)
} else {
    message("The mode was invalid")

    quit(status=1)
}