extends SceneTree

# Rendered-screenshot helper adapted from GameCraft-Bench tools/screenshot.gd:
# https://github.com/FreedomIntelligence/gamecraft-bench
# Licensed under Apache-2.0.

const DEFAULT_FRAMES := 30


func _initialize() -> void:
	var args := _parse_args(OS.get_cmdline_user_args())
	var out_path: String = args.get("out", "")
	if out_path.is_empty():
		push_error("capture_screenshot.gd: --out <path> is required")
		quit(2)
		return

	var frames: int = int(args.get("frames", DEFAULT_FRAMES))
	if frames < 1:
		push_error("capture_screenshot.gd: --frames must be positive")
		quit(2)
		return

	var scene_path: String = args.get(
		"scene", ProjectSettings.get_setting("application/run/main_scene", "")
	)
	if scene_path.is_empty():
		push_error("capture_screenshot.gd: no scene specified and project has no main scene")
		quit(2)
		return

	var packed: PackedScene = load(scene_path)
	if packed == null:
		push_error("capture_screenshot.gd: failed to load scene %s" % scene_path)
		quit(3)
		return

	var instance: Node = packed.instantiate()
	root.add_child(instance)
	for _frame in range(frames):
		await process_frame

	var image: Image = root.get_viewport().get_texture().get_image()
	if image == null:
		push_error("capture_screenshot.gd: viewport returned no image")
		quit(4)
		return

	var error: int = image.save_png(out_path)
	if error != OK:
		push_error("capture_screenshot.gd: save_png returned %d for %s" % [error, out_path])
		quit(5)
		return

	print("screenshot saved: %s (%dx%d)" % [out_path, image.get_width(), image.get_height()])
	quit(0)


func _parse_args(argv: PackedStringArray) -> Dictionary:
	var parsed := {}
	var index := 0
	while index < argv.size():
		var argument: String = argv[index]
		if not argument.begins_with("--"):
			index += 1
			continue
		var key: String = argument.substr(2)
		var value := "true"
		if "=" in key:
			var parts: PackedStringArray = key.split("=", true, 1)
			key = parts[0]
			value = parts[1]
		elif index + 1 < argv.size() and not argv[index + 1].begins_with("--"):
			value = argv[index + 1]
			index += 1
		parsed[key] = value
		index += 1
	return parsed
