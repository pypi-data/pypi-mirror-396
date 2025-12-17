## Basic model info

Model name: digital-prairie-labs/spring-wedding
Model description: None


## Model inputs

- prompt (required): Prompt for generated image. If you include the `trigger_word` used in the training process you are more likely to activate the trained object, style, or concept in the resulting image. (string)
- image (optional): Input image for image to image or inpainting mode. If provided, aspect_ratio, width, and height inputs are ignored. (string)
- mask (optional): Image mask for image inpainting mode. If provided, aspect_ratio, width, and height inputs are ignored. (string)
- aspect_ratio (optional): Aspect ratio for the generated image. If custom is selected, uses height and width below & will run in bf16 mode (string)
- height (optional): Height of generated image. Only works if `aspect_ratio` is set to custom. Will be rounded to nearest multiple of 16. Incompatible with fast generation (integer)
- width (optional): Width of generated image. Only works if `aspect_ratio` is set to custom. Will be rounded to nearest multiple of 16. Incompatible with fast generation (integer)
- prompt_strength (optional): Prompt strength when using img2img. 1.0 corresponds to full destruction of information in image (number)
- model (optional): Which model to run inference with. The dev model performs best with around 28 inference steps but the schnell model only needs 4 steps. (string)
- num_outputs (optional): Number of outputs to generate (integer)
- num_inference_steps (optional): Number of denoising steps. More steps can give more detailed images, but take longer. (integer)
- guidance_scale (optional): Guidance scale for the diffusion process. Lower values can give more realistic images. Good values to try are 2, 2.5, 3 and 3.5 (number)
- seed (optional): Random seed. Set for reproducible generation (integer)
- output_format (optional): Format of the output images (string)
- output_quality (optional): Quality when saving the output images, from 0 to 100. 100 is best quality, 0 is lowest quality. Not relevant for .png outputs (integer)
- disable_safety_checker (optional): Disable safety checker for generated images. (boolean)
- go_fast (optional): Run faster predictions with model optimized for speed (currently fp8 quantized); disable to run in original bf16 (boolean)
- megapixels (optional): Approximate number of megapixels for generated image (string)
- lora_scale (optional): Determines how strongly the main LoRA should be applied. Sane results between 0 and 1 for base inference. For go_fast we apply a 1.5x multiplier to this value; we've generally seen good performance when scaling the base value by that amount. You may still need to experiment to find the best value for your particular lora. (number)
- extra_lora (optional): Load LoRA weights. Supports Replicate models in the format <owner>/<username> or <owner>/<username>/<version>, HuggingFace URLs in the format huggingface.co/<owner>/<model-name>, CivitAI URLs in the format civitai.com/models/<id>[/<model-name>], or arbitrary .safetensors URLs from the Internet. For example, 'fofr/flux-pixar-cars' (string)
- extra_lora_scale (optional): Determines how strongly the extra LoRA should be applied. Sane results between 0 and 1 for base inference. For go_fast we apply a 1.5x multiplier to this value; we've generally seen good performance when scaling the base value by that amount. You may still need to experiment to find the best value for your particular lora. (number)


## Model output schema

{
  "type": "array",
  "items": {
    "type": "string",
    "format": "uri"
  },
  "title": "Output"
}

If the input or output schema includes a format of URI, it is referring to a file.


## Example inputs and outputs

Use these example outputs to better understand the types of inputs the model accepts, and the types of outputs the model returns:

### Example (https://replicate.com/p/82rbtb3e71rma0cqpw19wq9018)

#### Input

```json
{
  "model": "dev",
  "prompt": "TOK A minimalist wedding bouquet with large white flowers with pops of pale pink, mauve, red burgundy, and pale yellow with green greenery. It's tall and airy, but it also has large fluffy flowers. It also has pops of small periwinkle blue flowers.",
  "go_fast": false,
  "lora_scale": 1,
  "megapixels": "1",
  "num_outputs": 1,
  "aspect_ratio": "1:1",
  "output_format": "webp",
  "guidance_scale": 3,
  "output_quality": 80,
  "prompt_strength": 0.8,
  "extra_lora_scale": 1,
  "num_inference_steps": 28
}
```

#### Output

```json
[
  "https://replicate.delivery/xezq/tXYYPPKDBpLGENScQjDfreg7hAhyTBrEIquqpBeUevVnqstTB/out-0.webp"
]
```


## Model readme

> No readme available for this model.

