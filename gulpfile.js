'use strict';

var importOnce = require('node-sass-import-once'),
  path = require('path');

var options = {};

// #############################
// Edit these paths and options.
// #############################

// The root paths are used to construct all the other paths in this
// configuration. The "project" root path is where this gulpfile.js is located.
options.rootPath = {
  project     : __dirname + '/',
  app         : __dirname + '/opentech/',
  theme       : __dirname + '/opentech/static_src/'
};

options.theme = {
  root      : options.rootPath.theme,
  sass      : options.rootPath.theme + 'src/sass/',
  js        : options.rootPath.theme + 'src/javascript/',
  img       : options.rootPath.theme + 'src/images/',
  font      : options.rootPath.theme + 'src/fonts/',
  dest      : options.rootPath.app   + 'static_compiled/',
  css       : options.rootPath.app   + 'static_compiled/css/',
  js_dest   : options.rootPath.app   + 'static_compiled/js/',
  img_dest  : options.rootPath.app   + 'static_compiled/images/',
  font_dest : options.rootPath.app   + 'static_compiled/fonts/'
};

// Define the node-sass configuration. The includePaths is critical!
options.sass = {
  importer: importOnce,
  includePaths: [
    options.theme.sass,
  ],
  outputStyle: 'expanded'
};

// Define the paths to the JS files to lint.
options.eslint = {
  files  : [
    options.theme.js + '**/*.js',
    '!' + options.theme.js + '**/*.min.js'
  ]
};

// If your files are on a network share, you may want to turn on polling for
// Gulp watch. Since polling is less efficient, we disable polling by default.
options.gulpWatchOptions = {interval: 600};
// options.gulpWatchOptions = {interval: 1000, mode: 'poll'};


// Load Gulp and tools we will use.
var gulp      = require('gulp'),
  $           = require('gulp-load-plugins')(),
  del         = require('del'),
  // gulp-load-plugins will report "undefined" error unless you load gulp-sass manually.
  sass        = require('gulp-sass'),
  cleanCSS    = require('gulp-clean-css'),
  touch       = require('gulp-touch-cmd');

// The sass files to process.
var sassFiles = [
  options.theme.sass + '**/*.scss',
  // Do not open Sass partials as they will be included as needed.
  '!' + options.theme.sass + '**/_*.scss'
];

// Clean CSS files.
gulp.task('clean:css', function clean () {
  return del([
      options.theme.css + '**/*.css',
      options.theme.css + '**/*.map'
    ], {force: true});
});

// Clean JavaScript files.
gulp.task('clean:js', function clean () {
  return del([
      options.theme.js_dest + '**/*.js',
      options.theme.js_dest + '**/*.map'
    ], {force: true});
});

// Clean all directories.
gulp.task('clean', gulp.parallel('clean:css', 'clean:js'));

// Lint JavaScript.
gulp.task('lint:js', function lint () {
  return gulp.src(options.eslint.files)
    .pipe($.eslint())
    .pipe($.eslint.format());
});

// Lint JavaScript and throw an error for a CI to catch.
gulp.task('lint:js-with-fail', function lint () {
  return gulp.src(options.eslint.files)
    .pipe($.eslint())
    .pipe($.eslint.format())
    .pipe($.eslint.failOnError());
});

// Lint Sass.
gulp.task('lint:sass', function lint () {
  return gulp.src(options.theme.sass + '**/*.scss')
    .pipe($.sassLint())
    .pipe($.sassLint.format());
});

// Lint Sass and throw an error for a CI to catch.
gulp.task('lint:sass-with-fail', function lint () {
  return gulp.src(options.theme.sass + '**/*.scss')
    .pipe($.sassLint())
    .pipe($.sassLint.format())
    .pipe($.sassLint.failOnError());
});

// Lint Sass and JavaScript.
gulp.task('lint', gulp.parallel('lint:sass', 'lint:js'));

// Build CSS.
gulp.task('styles', gulp.series('clean:css', function css () {
  return gulp.src(sassFiles)
    .pipe($.sourcemaps.init())
    .pipe(sass(options.sass).on('error', sass.logError))
    .pipe($.size({showFiles: true}))
    .pipe($.sourcemaps.write('./'))
    .pipe(gulp.dest(options.theme.css))
    .pipe(touch());
}));

gulp.task('styles:production', gulp.series('clean:css', function css () {
  return gulp.src(sassFiles)
    .pipe(sass(options.sass).on('error', sass.logError))
    .pipe(cleanCSS({rebase: false}))
    .pipe($.size({showFiles: true}))
    .pipe(gulp.dest(options.theme.css))
    .pipe(touch());
}));

// Build JavaScript.
gulp.task('scripts', gulp.series('clean:js', function js () {
  return gulp.src(options.theme.js + '**/*.js')
    .pipe($.sourcemaps.init())
    .pipe($.babel({presets: ['@babel/env']}))
    .pipe($.size({showFiles: true}))
    .pipe($.sourcemaps.write('./'))
    .pipe(gulp.dest(options.theme.js_dest));
}));

// Build JavaScript.
gulp.task('scripts:production', gulp.series('clean:js', function js () {
  return gulp.src(options.theme.js + '**/*.js')
    .pipe($.babel({presets: ['@babel/env']}))
    .pipe($.uglify())
    .pipe($.size({showFiles: true}))
    .pipe(gulp.dest(options.theme.js_dest));
}));

// Copy images.
gulp.task('images', function copy () {
  return gulp.src(options.theme.img + '**/*.*').pipe(gulp.dest(options.theme.img_dest));
});

// Copy fonts.
gulp.task('fonts', function copy () {
  return gulp.src(options.theme.font + '**/*.*').pipe(gulp.dest(options.theme.font_dest));
});

// Run Djangos collectstatic command.
gulp.task('collectstatic', function exec () {
  return gulp.src(options.theme.font + '**/*.*').pipe($.exec('python manage.py  collectstatic --noinput -v0'));
});

// Watch for changes and rebuild.
gulp.task('watch:css', gulp.series('styles', function watch () {
  return gulp.watch(options.theme.sass + '**/*.scss', options.gulpWatchOptions, gulp.series('styles'));
}));

gulp.task('watch:lint:sass', gulp.series('lint:sass', function watch () {
  return gulp.watch(options.theme.sass + '**/*.scss', options.gulpWatchOptions, gulp.series('lint:sass'));
}));

gulp.task('watch:lint:js', gulp.series('lint:js', function watch () {
  return gulp.watch(options.eslint.files, options.gulpWatchOptions, gulp.series('lint:js'));
}));

gulp.task('watch:js', gulp.series('scripts', function watch () {
  return gulp.watch(options.eslint.files, options.gulpWatchOptions, gulp.series('scripts'));
}));

gulp.task('watch:images', gulp.series('images', function watch () {
  return gulp.watch(options.theme.img + '**/*.*', options.gulpWatchOptions, gulp.series('images'));
}));

gulp.task('watch:fonts', gulp.series('fonts', function watch () {
  return gulp.watch(options.theme.font + '**/*.*', options.gulpWatchOptions, gulp.series('fonts'));
}));

gulp.task('watch:static', gulp.series('collectstatic', function watch () {
  return gulp.watch(options.theme.dest + '**/*.*', options.gulpWatchOptions, gulp.series('collectstatic'));
}));

gulp.task('watch', gulp.parallel('watch:css', 'watch:lint:sass', 'watch:js', 'watch:lint:js', 'watch:images', 'watch:fonts', 'watch:static'));

// Build everything.
gulp.task('build', gulp.parallel('styles:production', 'scripts:production', 'images', 'fonts', 'lint'));

// Deploy everything.
gulp.task('deploy', gulp.parallel('styles:production', 'scripts:production', 'images', 'fonts'));

// The default task.
gulp.task('default', gulp.series('build'));


// Resources used to create this gulpfile.js:
// - https://github.com/google/web-starter-kit/blob/master/gulpfile.babel.js
// - https://github.com/dlmanning/gulp-sass/blob/master/README.md
