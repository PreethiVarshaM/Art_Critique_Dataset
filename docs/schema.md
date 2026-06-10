# Dataset Schema

Each row represents one artwork selected from an existing source dataset, plus your added critique labels.

| Column | Required | Description |
| --- | --- | --- |
| `id` | yes | Internal stable ID, such as `ACD_000001`. |
| `source` | yes | Source dataset, such as `wikiart`, `artelingo`, or `semart`. |
| `source_id` | no | Original dataset ID, slug, filename, or URL-safe identifier. |
| `image_path` | yes | Local image path relative to this repo or source dataset root. |
| `image_url` | no | Original public URL if available. |
| `artist` | no | Artist name from the source dataset. |
| `style` | no | Style label, for example `Impressionism`. |
| `genre` | no | Genre label, for example `portrait` or `landscape`. |
| `emotion` | no | Emotion label, especially if merged from ArtELingo. |
| `description` | no | Existing caption or short description. |
| `composition` | yes | `good`, `average`, or `weak`. |
| `color_harmony` | yes | `good`, `average`, or `weak`. |
| `contrast` | yes | `high`, `medium`, or `low`. |
| `lighting` | yes | `good`, `flat`, or `unclear`. |
| `perspective` | yes | `correct`, `slightly_wrong`, `wrong`, or `not_applicable`. |
| `critique_notes` | no | Human-written notes explaining the labels. |
| `split` | no | `train`, `validation`, or `test`. |

## Example

```csv
id,source,source_id,image_path,image_url,artist,style,genre,emotion,description,composition,color_harmony,contrast,lighting,perspective,critique_notes,split
ACD_000001,wikiart,monet_water_lilies,data/raw/wikiart/monet_water_lilies.jpg,,Claude Monet,Impressionism,landscape,calm,"Soft garden scene",good,good,medium,good,not_applicable,"Strong mood and color unity; perspective is not central to critique.",train
```
