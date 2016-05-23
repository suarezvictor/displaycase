upload:
	chmod ugo+r *
	rsync -HPavz .  hands.com:public_html/eoma/kde_tablet/3dcase
