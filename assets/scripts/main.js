/* ========================================================================
 * DOM-based Routing
 * Based on http://goo.gl/EUTi53 by Paul Irish
 *
 * Only fires on body classes that match. If a body class contains a dash,
 * replace the dash with an underscore when adding it to the object below.
 *
 * .noConflict()
 * The routing is enclosed within an anonymous function so that you can
 * always reference jQuery with $, even when in .noConflict() mode.
 * ======================================================================== */

(function($) {

  // Use this variable to set up the common and page specific functions. If you
  // rename this variable, you will also need to rename the namespace below.
  var Rikleimt = {
    // All pages
    'common': {
      init: function() {
        // JavaScript to be fired on all pages

        // Add 'js' class on HTML tag
        $('html').addClass('js');

        // Add element so we can change its layout in CSS and have a better way
        // to trigger narrow resolution (or any other where there's no other way)
        $('body').append('<div id="responsiveResTrig"></div>');

        $(window).on('resize', function(){
          UTIL.fire('common', 'setResponsiveClasses');
        }).resize();

        // Main nav
        UTIL.fire('common', 'mainnav');

        // MatchHeight functions
        UTIL.fire('common', '_matchHeight');
      },

      finalize: function() {
        // JavaScript to be fired on all pages, after page specific JS is fired

        // Close mainnav
        setTimeout(function() {
          $('#mainnav').removeClass('opened');
        }, 1000);
      },
      setResponsiveClasses: function(){
        // Add or remove classes on window resize
        var availableSizes = ['mobile','tablet','narrow','wide','extrawide'];

        keepSelectedSizeOnly = function(size){
          for (a = 0; a < availableSizes.length; ++a) {
            if (availableSizes[a] != size){ $('body').removeClass(availableSizes[a]);}
          }
          $('body').addClass(size);
        };

        setSize = function(size){
          // If the site doesn't already have the correct class
          if((!$('body.'+size).length)){

            if(size == 'mobile'){
              keepSelectedSizeOnly('mobile');
            }else{
              // Close the mobile nav
              keepSelectedSizeOnly(size);
            }
          }
        };

        // is mobile
        if($('#responsiveResTrig').css('width') == '50px') {
          setSize('mobile');
        }
        // is tablet resolution
        else if($('#responsiveResTrig').css('width') == '75px') {
          setSize('tablet');
        }
        // is wide resolution
        else if($('#responsiveResTrig').css('width') == '200px') {
          setSize('wide');
        }
        // is extra-wide resolution
        else if($('#responsiveResTrig').css('width') == '300px') {
          setSize('extrawide');
        }
        // is narrow resolution
        else {
          setSize('narrow');
        }
      },
      mainnav: function() {
        // Main nav

        $('#mainnav button').click(function(){
          $('#mainnav').toggleClass('opened');

          $(this).blur();
        });

        $('#mainnav').swipeleft(function(){
          $('#mainnav').addClass('opened');
        });
        $('#mainnav').swiperight(function(){
          $('#mainnav').removeClass('opened');
        });
      },

      _matchHeight: function() {

      }
    },

    // Home page
    'is_home': {
      init: function() {
        // JavaScript to be fired on the home page
      },

      finalize: function() {
        // JavaScript to be fired on the home page, after the init JS
      },
    },

    // Book page
    'is_book': {
      init: function() {
        // JavaScript to be fired on the book page

        // Setup the book
        UTIL.fire('is_book', 'setupBook');
      },

      setupBook: function() {
        // Setup the book

        // Prepare the Wiki box
        var $wikibox = $("#wikibox");

        $wikibox.draggable({
          containment: 'body',
          cancel: '#wikibox .wrap, #wikibox .close'
        });

        // Clone the book to apply WowBook only on some resolutions more easily
        $('#content section.book > .content').clone().attr('id', 'mybook').removeClass('content').appendTo($("#content section.book"));

        // Do the actual setup
        var root = 'https://jsonplaceholder.typicode.com';

        var book = $('#mybook').wowBook({
          width: 1140,
          height: 700,
          thumbnailsPosition: 'bottom',
          // flipSound: false,
          flipSoundFile: [
            "page-flip.mp3",
            "page-flip.ogg"
          ],
          flipSoundPath: "/static/plugins/wow_book/sound/",
          scaleToFit: "section.book",
          centeredWhenClosed: true,
          responsiveHandleWidth: 30,
          toolbar: "lastLeft, left, right, lastRight, toc, zoomin, zoomout, flipsound, thumbnails",
          responsiveSinglePage: function( book ){
            // return true (and activate single page mode)
            return $("body.tablet").length;
          },
          onShowPage: function(book,page, pageIndex) {
            //console.log(book);
            if(pageIndex == book.pages.length-2){
              $.ajax({ //the internals of this ajax call should be replaced at some point
                url: root + '/posts/1',
                method: 'GET'
              }).then(function(data) {
                // console.log(data.body);
                book.insertPage("<div>"+data.body+"</div>");
                book.insertPage("<div> This is the other page </div>");
              });
            }

            // Tooltips (Trig translations)
            $('[data-toggle="tooltip"]').tooltip({
              placement: 'top auto',
              viewport: 'section.book'
            });

            $('[data-toggle="tooltip"]').click(function(){
              $(this).blur();

              return false;
            });


            // Use the Wiki box
            $('[data-toggle="wikibox"]').click(function(){
              // Change the box contents
              // [...]

              // Calculate the content box height from the title height
              $wikibox.find('.content').css({
                height: ($wikibox.find('.wrap').outerHeight() - $wikibox.find('header').outerHeight()) + 'px'
              });

              // Show
              $wikibox.addClass('opened');

              $(this).blur();

              return false;
            });

            // Hide the Wiki box
            $wikibox.find('.close button').click(function(){
              $wikibox.removeClass('opened');

              $(this).blur();

              return false;
            });

            $wikibox.find('.wrap > header').swipedown(function(){
              $wikibox.removeClass('opened');
            });
          },
        }, function(){
          book.showThumbnails();
          book.showLightbox();

          $(".wowbook-lightbox > .wowbook-close").remove(); // remove lightbox's close button

          book.updateBook();
        });
      },

      finalize: function() {
        // JavaScript to be fired on the book page, after the init JS
      },
    }
  };

  // The routing fires all common scripts, followed by the page specific scripts.
  // Add additional events for more control over timing e.g. a finalize event
  var UTIL = {
    fire: function(func, funcname, args) {
      var fire;
      var namespace = Rikleimt;
      funcname = (funcname === undefined) ? 'init' : funcname;
      fire = func !== '';
      fire = fire && namespace[func];
      fire = fire && typeof namespace[func][funcname] === 'function';

      if (fire) {
        namespace[func][funcname](args);
      }
    },
    loadEvents: function() {
      // Fire common init JS
      UTIL.fire('common');

      // Fire page-specific init JS, and then finalize JS
      $.each(document.body.className.replace(/-/g, '_').split(/\s+/), function(i, classnm) {
        UTIL.fire(classnm);
        UTIL.fire(classnm, 'finalize');
      });

      // Fire common finalize JS
      UTIL.fire('common', 'finalize');
    },
  };

  // Load Events
  $(document).ready(UTIL.loadEvents);

})(jQuery); // Fully reference jQuery after this point.
