var utils = require('users/robertmsare/channel-classifier-js:utils.js');

var muni = ee.FeatureCollection('users/robertmsare/countries/brazil_municipalities')
var dengue = ee.FeatureCollection('users/robertmsare/data/brazil_dengue_PLOSOne')

var calcwater = function(image) {
  var permanent = image.eq(1).rename(['water']);
  var pixels = image.neq(1).rename(['pixels']);
  return image.addBands(permanent).addBands(pixels).select(['water', 'pixels']);
}

var years = utils.range(2002, 2012)
var nyears = years.length

var max_months = 4;
var min_months = 1;

for(var i = 0; i < nyears; i++) {
  var year = years[i]
  var start_date = year.toString() + '-01-01'
  var end_date = (year + 1).toString() + '-01-01'
  var jrc = ee.ImageCollection('JRC/GSW1_0/MonthlyHistory').filterDate(start_date, end_date)
  var counts = jrc.map(function(im) { im = im.remap([1, 2], [0, 1], 0)
                               return im
  })

  var months_water = counts.sum().rename(['water'])
  var seasonal_water = months_water.gte(min_months).and(months_water.lte(max_months))

  muni = seasonal_water.reduceRegions({
    collection: muni,
    reducer: ee.Reducer.sum(),
    scale: 300
  });
  
  var calcprop = function(feature) {
    var value = feature.get('water')//.divide(feature.get('pixels')).multiply(100))
    return feature.set('water_' + year.toString(), value)
  }
  
  muni = muni.map(calcprop)
}

Export.table.toDrive({
  collection: muni,
  description: 'brazil_seasonal_water',
  fileFormat: 'GeoJSON'
})
