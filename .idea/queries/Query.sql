UPDATE plan_visual_django_plotablestyle
SET style_name = REPLACE(style_name, 'app-app-app-app-theme-01', 'app-theme-01')
WHERE style_name LIKE '%app-app-app-app-theme-01%';

