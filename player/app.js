(function(angular){

  'use strict';

  var app = angular.module('test.player', ['ov.player']);

  app.controller('TestController', TestController);
  TestController.$inject = ['$scope', '$window', '$location'];

  /**
   * Defines the test controller.
   */
  function TestController($scope, $window, $location){
    $scope.ready = true;
    $scope.data =
      {
        mediaId : '136081112', // The id of the video on youtube platform
        timecodes : { // Timecodes
          0 : { // Timecode in milliseconds (0 ms)
            image : { // Image to display at 0 ms
              small : 'slide_00000.jpeg', // Small version of the image
              large : 'slide_00000_large.jpeg' // Large version of the image
            }
          },
          1200 : { // Timecode in milliseconds (1200 ms)
            image : { // Image to display at 1200 ms
              small : 'slide_00001.jpeg', // Small version of the image
              large : 'slide_00001_large.jpeg' // Large version of the image
            }
         }
         ...
       },
       chapters : [ // Chapters
         {
           name : 'Chapter 1', // Chapter name
           description : 'Chapter 1 description', // Chapter description
           value : 0.04 // Chapter timecode in percent (percentage of the video)
         },
         {
           name : 'Chapter 2', // Chapter name
           description : 'Chapter 2 description', // Chapter description
           value : 0.3 // Chapter timecode in percent (percentage of the video)
         }
         ...
       ],
       cut : [ // Cut information (begin and end)
         {
           type : 'begin', // Cut type
           value : 0 // Begin timecode (percentage of the media)
         },
         {
           type : 'end', // Cut type
           value : 0.9 // End timecode (percentage of the media)
         }
       ]
     };
  }

})(angular);
