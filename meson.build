project(
  'cys403_project',
  version : '0.1.0',
  license : 'GPL3',
  default_options : ['warning_level=2'],
)

DEVELOPER_ID = 'io.github.zefr0x'
BASE_ID = DEVELOPER_ID + '.' + meson.project_name()
APP_ID = BASE_ID
APP_BIN = 'cys403_project'
APP_VERSION = meson.project_version()

# Get options
prefix = get_option('prefix')
datadir = prefix / get_option('datadir')
bindir = prefix / get_option('bindir')
libdir = prefix / get_option('libdir')
localedir = prefix / get_option('localedir')
profile = get_option('profile')

if profile == 'development'
	APP_VERSION += '-' + run_command(
		'git', 'rev-parse', '--short', 'HEAD',
		check: true
	).stdout().strip()
	APP_ID += '.' + 'Devel'
endif

# Imports
gnome = import('gnome')

# Check for deps
gtk4 = dependency('gtk4', version: '>= 4.0')
libadwaita = dependency('libadwaita-1', version: '>= 1.7')

# Post install
gnome.post_install(
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)

# Other meson.build sub files
subdir('data/')
subdir('po/')
subdir('cys403_project/')
