library(tidyverse)
library(sp)
library(raster)
library(rgeos)
library(rgbif)
library(viridis)
library(gridExtra)
library(rasterVis)
library(rgdal)
library(USAboundaries)
library(USAboundariesData)

library(tigris)

set.seed(1)

## function to create hexagons
## all credit to: http://strimas.com/spatial/hexagonal-grids/

make_grid <- function(x, cell_diameter, cell_area, clip = FALSE) {
  if (missing(cell_diameter)) {
    if (missing(cell_area)) {
      stop("Must provide cell_diameter or cell_area")
    } else {
      cell_diameter <- sqrt(2 * cell_area / sqrt(3))
    }
  }
  ext <- as(extent(x) + cell_diameter, "SpatialPolygons")
  projection(ext) <- projection(x)
  # generate array of hexagon centers
  g <- spsample(ext, type = "hexagonal", cellsize = cell_diameter, 
                offset = c(0.5, 0.5))
  # convert center points to hexagons
  g <- HexPoints2SpatialPolygons(g, dx = cell_diameter)
  # clip to boundary of study area
  if (clip) {
    g <- gIntersection(g, x, byid = TRUE)
  } else {
    g <- g[x, ]
  }
  # clean up feature IDs
  row.names(g) <- as.character(1:length(g))
  return(g)
}

## load dc boundary shape file

states <- states(cb = TRUE)

dmv <- subset(states,STATEFP == "51" | STATEFP == "11" | STATEFP == "24")

dmv_boundary <- dmv %>%
    disaggregate %>% 
    geometry

dmv_boundary <- sapply(dmv_boundary@polygons, slot, "area") %>% 
    {which(. == max(.))} %>% 
  dmv_boundary[.]

dmv_boundary_utm <- CRS("+proj=utm +zone=44 +datum=WGS84 +units=km +no_defs") %>% 
  spTransform(dmv_boundary, .)

hex_grid <- make_grid(dmv_boundary_utm, cell_area = .5, clip = TRUE)

## export hexes as shapefile

raster::shapefile(hex_grid, "hex-grid.shp")

## read back in to verify

dc_hexes <- readOGR("C:/Users/augus/OneDrive/Documents",
                       layer="hex-grid")
