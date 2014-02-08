/*
 * Bootstrap Image Gallery JS Demo 3.0.0
 * https://github.com/blueimp/Bootstrap-Image-Gallery
 *
 * Copyright 2013, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint unparam: true */
/*global window, document, blueimp, $ */

$(function () {
    'use strict';

    $('#borderless-checkbox').on('change', function () {
      var borderless = $(this).is(':checked');
      $('#blueimp-gallery').data('useBootstrapModal', !borderless);
      $('#blueimp-gallery').toggleClass('blueimp-gallery-controls', borderless);
    });

    $('#fullscreen-checkbox').on('change', function () {
      $('#blueimp-gallery').data('fullScreen', $(this).is(':checked'));
    });

    $('#image-gallery-button').on('click', function (event) {
      event.preventDefault();
      blueimp.Gallery($('#links a'), $('#blueimp-gallery').data());
    });

    $('.select-photo').change(function() {
      // check if add to album button has to be enabled/disabled
      var abutton = $('#add-to-album-button');
      var is_checked = $('.select-photo').is(':checked');
      abutton.prop('disabled', !is_checked);
    });

    $('#add-to-album-button').click(function() {
      window.pbn = window.pbn || {};
      window.pbn.selected_photos = [];
      $.each($('.select-photo:checked'), function(idx, elt){
        window.pbn.selected_photos.push($(this).val());
      });
    });

    $('#add-to-album-form').submit(function(event) {
      event.preventDefault();
      var existing = $.trim($('#select-existing-album').val());
      var new_album = $.trim($('#create-new-album').val());
      if (existing === '' && new_album === '') {
        alert('Choisissez un album');
        return false;
      }
      $('#add-to-album-submit').prop('disabled', true);
      $('#add-to-album-submit').html('Sauvegarde...');
      var album_name = existing !== "" ? existing : new_album;
      var data = {
        photos: window.pbn.selected_photos,
        existing: (existing !== ""),
        album_name: album_name
      };
      $.post('/add_to_album', data, function(ret){
        alert("C'est fait !");
        $('#add-to-album-modal').modal('hide');
      });
    });

    $("#menu-toggle").click(function(e) {
      e.preventDefault();
      $("#wrapper").toggleClass("active");
    });

});
