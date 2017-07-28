$(document).ready(function(){
   var $grid = $('.grid').isotope({
  // main isotope options
  itemSelector: '.grid-item',
  // set layoutMode
  layoutMode: 'cellsByRow',
  // options for cellsByRow layout mode
  cellsByRow: {
    columnWidth: 200,
    rowHeight: 150
  },
  // options for masonry layout mode
  masonry: {
    columnWidth: '.grid-sizer'
  }
})
});