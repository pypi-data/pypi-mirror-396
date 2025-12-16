# Work with Semantics API

The Panoramax API offer various levels of [Semantics](https://docs.panoramax.fr/tags/) to help describe what's visible inside the pictures.

You can find semantics in:

- :material-upload: **Upload sets**, for generic metadata applying to all pictures you send
- :fontawesome-solid-images: **Collections / Sequences**, for common metadata accross many pictures
- :material-image: **Items / Pictures**, for specific context of a single picture
- :material-vector-square: **Annotations**, for outlining part of a single picture

[They mainly consist in a succession of tags](https://docs.panoramax.fr/tags/syntax/), in a similar fashion of OpenStreetMap's tags.

## :computer: Structure of semantics in responses

API routes retrieving collections, items or annotations share a __common format__, stored as `semantics` property. For example:

```json
{
	"semantics": [
		{ "key": "osm|traffic_sign", "value": "stop" },
		{ "key": "detection_model[osm|traffic_sign]", "value": "SGBlur/1.0.0" }
	]
}
```

A `semantics` array list each individual tag (key/value) available for the object. Note that __keys can be present several times__ (contrarily to OpenStreetMap), but the key/value pair needs to be unique. For example, if hashtags are set on a picture:

```json
{
	"semantics": [
		{ "key": "hashtag", "value": "PanneauBiche" },
		{ "key": "hashtag", "value": "Panneauramax" }
	]
}
```

You can find them in the following API routes:

- `GET /api/upload_sets/{uploadSetId}`
- `GET /api/collections/{collectionId}`
- `GET /api/collections/{collectionId}/items/{itemId}` (or `GET /api/pictures/{itemId}`)
- `GET /api/collections/{collectionId}/items/{itemId}/annotations/{annotationId}` (or `GET /api/annotations/{annotationId}`)

## :pencil: Editing object's semantics

You can as well __create and edit__ your own semantics on pictures, sequences and annotations. All available routes are [listed in our API documentation](https://panoramax.ign.fr/api/docs/swagger#/Semantics).

The semantics update logic we use is :octicons-file-diff-16: _differential_ (or _atomic_): you only list the tags you want to add or delete. You __don't have to repeat all existing tags__ of the feature.

- :white_check_mark: This logic is __similar__ to a patch file logic, or to a git commit, which only needs a delta of changes.
- :fontawesome-solid-times-square: This logic is __different__ from the OSM API, which expects you to always list all tags you want to end with.

!!! note

	Compared to semantics format in API responses, when you edit semantics another property named `action` is available, to say if you either want to `add` or `delete` the tag you're listing. If missing, action is `add` by default.

Let's see some examples.

### :fontawesome-solid-images: :red_car: Set transport mode at upload

The website upload page allows you to change the transport mode used for capturing a sequence. This is done through the API, when setting the _Upload set_ metadata. For example, when you create an Upload set, beyond other parameters you can set `semantics` and add the transport mode:

```bash
curl -X POST "https://my-panoramax.fr/api/upload_sets" \
	-H "Authorization: Bearer YOUR_TOKEN_HERE" \
	-H "Content-Type: application/json" \
	--data '{
		...,
		"semantics": [
			{ "action": "add", "key": "transport", "value": "walk" }
		],
		...
	}'
```

!!! note

	You can use any key/value you like, even if you may try to use common defined ones to make sure people can actually re-use them. Check out [documented tags](https://docs.panoramax.fr/tags/syntax/#values) to see more examples.

### :postbox: Categorize a picture as having a post box

To make pictures easier to find, you can add generic tags that describe the picture as a whole. For example, we could add a tag on the picture to mark it as having a post box, without setting precisely where it is located in the image. This is usually done later, once all your uploads are finished, so using a `PATCH` over a picture:

```bash
curl -X PATCH "https://my-panoramax.fr/api/collections/1234/items/4567" \
	-H "Authorization: Bearer YOUR_TOKEN_HERE" \
	-H "Content-Type: application/json" \
	--data '{
		"semantics": [
			{ "action": "add", "key": "osm|amenity", "value": "post_box" }
		]
	}'
```

### :material-bench-back: Draw a bench on a picture

If you're willing to work with detection algorithm (aka :robot: _AI_), you may want to draw various features over pictures in order to train your algorithm. You can do it through the API by creating __Annotations__ on pictures.

The annotations needs two information to be created:

- :fontawesome-solid-tags: Semantics, in a similar fashion as seen before
- :material-shape-rectangle-plus: Shape, to locate it over the picture

The shape is expressed in pixel, with the origin on top-left corner. They can be defined either as a list of coordinates or a GeoJSON-like geometry:

- `[minx, miny, maxx, maxy]`
- `{ "type": "Polygon", "coordinates": [ [ [x1, y1], [x2, y2], ... ] ] }`

So, to add a bench on our image:

```bash
curl -X POST "https://my-panoramax.fr/api/collections/1234/items/4567/annotations" \
	-H "Authorization: Bearer YOUR_TOKEN_HERE" \
	-H "Content-Type: application/json" \
	--data '{
		"semantics": [
			{ "action": "add", "key": "osm|amenity", "value": "bench" }
		],
		"shape": [100,250,600,900]
	}'
```

### :octagonal_sign: Classify a traffic sign

Panoramax offers a basic detection of traffic signs on public instances. Oldest ones were only setting a basic `osm|traffic_sign=yes` value on an annotation. If you're willing to make this information more precise, you can replace existing tag of an annotation:

```bash
curl -X PATCH "https://my-panoramax.fr/api/collections/1234/items/4567/annotations/1789" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     --data '{
		"semantics": [
			{ "action": "delete", "key": "osm|traffic_sign", "value": "yes" },
			{ "action": "add", "key": "osm|traffic_sign", "value": "stop" },
			{ "action": "add", "key": "classification_model[osm|traffic_sign=stop]", "value": "MyModel/1.2.3" },
			{ "action": "add", "key": "classification_confidence[osm|traffic_sign=stop]", "value": "0.759" },
		]
	}'
```

!!! info

	An existing annotation's geometry cannot be changed, you can only update the list of associated tags. If you're willing to change an annotation geometry, you have to delete it and create another one.

## :information_source: General recommendations

### :robot: Automated edits, detections & classifications

If you're willing to run automated edits, for example apply on a large amount of pictures results of an automated detection or classification, we __strongly recommend__ that you use tags that allow to track your changes.

In particular, you can add _qualifiers_ for detection and classification, for example:

```
osm|traffic_sign=yes
detection_model[osm|traffic_sign=yes]=SGBlur/1.0.0
detection_confidence[osm|traffic_sign=yes]=0.999

osm|traffic_sign=FR:A15b
classification_model[osm|traffic_sign=FR:A15b]=Panoramax-Signs/0.1.0
classification_confidence[osm|traffic_sign=FR:A15b]=0.888
```

!!! info

	For more details about available Panoramax tags, please consult our [Tags documentation](https://docs.panoramax.fr/tags/syntax/#panoramax).
