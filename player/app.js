(function(angular){

  'use strict';

  var app = angular.module('test.player', ['ov.player']);

  app.controller('TestController', TestController);
  TestController.$inject = ['$scope', '$window', '$location', '$http'];

  /**
   * Defines the test controller.
   */
  function TestController($scope, $window, $location, $http){
    $scope.ready = true;
    $http.get('content/r19ZYySke.json').success(function(data) {
      $scope.data = data;
    });
  }

})(angular);
