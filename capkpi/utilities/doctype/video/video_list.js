finergy.listview_settings["Video"] = {
	onload: (listview) => {
		listview.page.add_menu_item(__("Video Settings"), function() {
			finergy.set_route("Form","Video Settings", "Video Settings");
		});
	}
}
