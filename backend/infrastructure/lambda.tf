resource "aws_lambda_function" "user_spotify_data_retrieval_lambda" {
  function_name = "user_spotify_data_retrieval_lambda"
  role          = aws_iam_role.user_spotify_data_retrieval_lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.user_spotify_data_retrieval_lambda.repository_url}:${var.image_tag}"

  memory_size = 512
  timeout     = 30

  architectures = ["arm64"]
}
