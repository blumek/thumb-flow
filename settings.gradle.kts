rootProject.name = "thumb-flow"

include(
    ":upload_handler",
    ":thumbnail_generator",
)

project(":upload_handler").projectDir = file("src/lambda/upload_handler")
project(":thumbnail_generator").projectDir = file("src/lambda/thumbnail_generator")

