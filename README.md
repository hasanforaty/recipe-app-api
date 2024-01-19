# Recipe API

Recipe API is a backend application that enables users to create, store, and manage recipes. It provides features such as user authentication, the ability to add tags and ingredients to each recipe, image uploads, and filtering based on tags. The entire functionality is containerized in a Docker image for easy deployment.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Authentication](#authentication)
- [Adding Tags and Ingredients](#adding-tags-and-ingredients)
- [Image Upload](#image-upload)
- [Filtering](#filtering)
- [Deodorization](#deodorization)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Recipe Management:** Create, store, and manage your recipes.
- **Tags and Ingredients:** Add tags and ingredients to each recipe for better organization.
- **User Authentication:** Secure access with token-based authentication using email and password.
- **Image Upload:** Attach images to your recipes.
- **Filtering:** Filter recipes based on tags.
- **Dockerization:** The entire application is containerized in a Docker image for easy deployment.

## Installation

Follow these steps to install and set up the Recipe API on your local machine.

```bash
# Clone the repository
git clone https://github.com/hasanforaty/recipe-app-api.git

# Navigate to the project directory
cd recipe-app-api

# Install dependencies
docker-compose build
```
## Usage
To run the Recipe API locally, use the following command:
```bash
docker-compose up
```
The API will be accessible at http://localhost:8000.

## Authentication

User authentication is based on tokens. To authenticate, include the token in the headers of your requests.

Example:
```http
GET /api/recipes
Authorization: Bearer YOUR_TOKEN_HERE
```
## Adding Tags and Ingredients

You can add tags and ingredients to a recipe by including them in the request payload.

Example:
```json
{
  "title": "Delicious Pasta",
  "tags": ["Italian", "Pasta"],
  "ingredients": ["Pasta", "Tomatoes", "Olive Oil"]
}
```
## Image Upload

To attach an image to your recipe, include the image file in your request payload.

Example:
```json
{
  "title": "Beautiful Cake",
  "image": "base64-encoded-image-data"
}
```
## Adding Tags and Ingredients

You can add tags and ingredients to a recipe by including them in the request payload.

Example:
```json
{
  "title": "Delicious Pasta",
  "tags": ["Italian", "Pasta"],
  "ingredients": ["Pasta", "Tomatoes", "Olive Oil"]
}
```
## Image Upload

To attach an image to your recipe, include the image file in your request payload.

Example:
```json
{
  "title": "Beautiful Cake",
  "image": "base64-encoded-image-data"
}
```
## Filtering

Filter recipes based on tags by making a GET request to `/api/recipes` with the desired tag as a query parameter.

Example:
```http
GET /api/recipes?tag=Italian
```
## Deodorization

The Recipe API is Dockerized. Build the Docker image and run the container:

```bash
# Build Docker image
docker build -t recipe-app-api .

# Run the Docker container
docker run -p 8000:8000 recipe-app-api
```

## Contributing

Contributions are welcome!

## License

This project is licensed under the [MIT License](LICENSE).


