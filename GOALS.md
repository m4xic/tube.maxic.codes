# Goals 🎯

This is a living document listing each of the goals I want to achieve with this project

## "What's the status of the Tube?" `☑️ /v1/status`

> What's the status of the Tube?
>
> *The Circle line has major delays and the Waterloo & City line is closed for the night. There's good service everywhere else.*

## "What's the status of the *service*?" `☑️ /v1/status/<service>`

> What's the status of the Hammersmith & City line?
>
> *The Hammersmith & City line has good service right now.*

Inform the user of any lines with minor/major delays or suspensions.

## "When's the next *service* from *station* (towards *station*)?"

> When's the next DLR from Mudchute?
>
> *The next DLR from Crossharbour towards Bank is in 3 minutes. The next DLR from Mudchute towards Lewisham is in 2 minutes.*

> When's the next DLR from Canary Wharf towards Lewisham?
>
> *The next DLR from Canary Wharf towards Lewisham is in 6 minutes.*

Inform the user when the next two services are from each platform at their specified station

## "When's the next *service*?"

> When's the next DLR?
>
> *From West India Quay, the next DLR towards Bank is in 4 minutes. The next DLR towards Lewisham is in 7 minutes.*

Get the user's geo-location, identify their nearest Tube station and inform them of the next two services from each platform