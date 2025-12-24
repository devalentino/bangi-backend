from wireup import service

from src.tracker.entities import TrackClick, TrackPostback


@service
class TrackService:
    def track_click(self, click_id: str, campaign_id: str, parameters: dict) -> None:
        click = TrackClick(click_id=click_id, campaign_id=campaign_id, parameters=parameters)
        click.save()

    def track_postback(self, click_id: str, parameters: dict) -> None:
        postback = TrackPostback(click_id=click_id, parameters=parameters)
        postback.save()
