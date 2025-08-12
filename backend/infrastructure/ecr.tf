resource "aws_ecr_repository" "user_spotify_data_retrieval_lambda" {
  name = "user-spotify-data-retrieval-lambda"

  tags = {
    "project" : "spotify-themes-analyser"
  }
}
