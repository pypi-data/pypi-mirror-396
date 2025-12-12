# dsetool.policy

Policy package for the **DS eTool** website.

## Overview

This package provides customizations for the Plone-based DS eTool site, adapting its behavior and appearance to meet project requirements.

## Customizations

### z3c.jbot

This package overrides the client login form using `z3c.jbot`.

### Views for custom Euphorie types

This package provides some views to be used in Quaive for some content types (Choice, Option and Recommendation) that at the time of writing are only presents in a `Euphorie` branch called `dsetool`.

### Custom workflow for the sector type

The country managers should be able to do much less than what they do on regular Euphorie installations.
In particular, they should be able to just maintain, extend and update the recommendation texts in the backend.
