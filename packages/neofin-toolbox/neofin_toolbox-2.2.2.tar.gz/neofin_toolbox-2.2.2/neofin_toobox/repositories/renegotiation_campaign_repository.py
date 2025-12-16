from typing import List, Dict, Any, Optional
from boto3.dynamodb.conditions import Key, Attr
import logging

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository
from neofin_toobox.models.renegotiation_campaign import RenegotiationCampaign

logger = logging.getLogger(__name__)


class RenegotiationCampaignRepository(DynamoDbRepository):
    """Repository class for renegotiation campaign data operations in DynamoDB."""

    GSI_COMPANY_ID = 'company_id'
    GSI_END_DATE = 'end_date'

    def __init__(self):
        """Initialize the renegotiation campaign repository."""
        super().__init__()
        self.table_renegotiation_campaign = self.resource.Table(TableConfigEnum.RENEGOTIATION_CAMPAIGNS)

    def put_renegotiation_campaign(self, renegotiation_campaign: RenegotiationCampaign) -> None:
        """Save a renegotiation campaign to DynamoDB.

        Args:
            renegotiation_campaign: The RenegotiationCampaign object to save

        Raises:
            Exception: If DynamoDB put operation fails
        """
        try:
            logger.debug(f"Saving renegotiation campaign: {renegotiation_campaign.id}")

            self.table_renegotiation_campaign.put_item(
                Item=renegotiation_campaign.model_dump()
            )

            logger.info(f"Successfully saved renegotiation campaign: {renegotiation_campaign.id}")

        except Exception as e:
            logger.error(f"Error saving renegotiation campaign {renegotiation_campaign.id}: {str(e)}")
            raise Exception(
                f"Problems putting renegotiation campaign {renegotiation_campaign.id} in Database: {str(e)}")

    def list_renegotiation_campaigns_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Retrieve all renegotiation campaigns by company ID.

        Args:
            company_id: The company identifier

        Returns:
            List of RenegotiationCampaign objects sorted by created_at

        Raises:
            Exception: If DynamoDB query fails
        """
        try:
            logger.debug(f"Querying renegotiation campaigns by company_id: {company_id}")

            campaign_items = self._query_campaigns_by_company(company_id)

            if not campaign_items:
                logger.info(f"No renegotiation campaigns found for company_id={company_id}")
                return []

            campaign_items.sort(key=lambda x: x['created_at'])

            logger.info(f"Company ID: {company_id} - Found {len(campaign_items)} renegotiation campaigns")

            return campaign_items

        except Exception as e:
            logger.error(f"Error listing renegotiation campaigns by company: company_id={company_id}, error={str(e)}")
            raise Exception(f"Problems listing renegotiation campaigns in Database: {str(e)}")

    def list_renegotiation_campaigns_by_end_date(self, end_date: str) -> List[Dict[str, Any]]:
        """Retrieve all renegotiation campaigns by end date.

        Args:
            end_date: The campaign end date

        Returns:
            List of RenegotiationCampaign objects

        Raises:
            Exception: If DynamoDB query fails
        """
        try:
            logger.debug(f"Querying renegotiation campaigns by end_date: {end_date}")

            campaign_items = self._query_campaigns_by_end_date(end_date)

            if not campaign_items:
                logger.info(f"No renegotiation campaigns found for end_date={end_date}")
                return []


            logger.info(f"Found {len(campaign_items)} renegotiation campaigns for end_date: {end_date}")

            return campaign_items

        except Exception as e:
            logger.error(f"Error listing renegotiation campaigns by end_date: end_date={end_date}, error={str(e)}")
            raise Exception(f"Problems listing renegotiation campaigns by end date {end_date} in Database: {str(e)}")

    def get_renegotiation_campaign_by_id(self, renegotiation_campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single renegotiation campaign by ID.

        Args:
            renegotiation_campaign_id: The campaign identifier

        Returns:
            RenegotiationCampaign object if found, None otherwise

        Raises:
            Exception: If DynamoDB get operation fails
        """
        try:
            logger.debug(f"Getting renegotiation campaign by id: {renegotiation_campaign_id}")

            response = self.table_renegotiation_campaign.get_item(
                Key={'id': renegotiation_campaign_id}
            )

            if 'Item' not in response:
                logger.info(f"No renegotiation campaign found for id={renegotiation_campaign_id}")
                return None

            campaign = response['Item']

            logger.info(f"Successfully retrieved renegotiation campaign: {renegotiation_campaign_id}")

            return campaign

        except Exception as e:
            logger.error(f"Error getting renegotiation campaign: id={renegotiation_campaign_id}, error={str(e)}")
            raise Exception(
                f"Problems getting renegotiation campaign {renegotiation_campaign_id} in Database: {str(e)}")

    def _query_campaigns_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Query all campaigns by company_id with pagination handling.

        Args:
            company_id: The company identifier

        Returns:
            List of campaign items from DynamoDB
        """
        campaign_items = []
        last_evaluated_key = None

        while True:
            query_params = {
                'IndexName': self.GSI_COMPANY_ID,
                'KeyConditionExpression': Key('company_id').eq(company_id)
            }

            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table_renegotiation_campaign.query(**query_params)

            # Add items if any exist
            if response.get('Count', 0) > 0:
                campaign_items.extend(response['Items'])

            # Check if there are more pages
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return campaign_items

    def _query_campaigns_by_end_date(self, end_date: str) -> List[Dict[str, Any]]:
        """Query all campaigns by end_date with pagination handling.

        Args:
            end_date: The campaign end date

        Returns:
            List of campaign items from DynamoDB
        """
        campaign_items = []
        last_evaluated_key = None

        while True:
            query_params = {
                'IndexName': self.GSI_END_DATE,
                'KeyConditionExpression': Key('end_date').eq(end_date)
            }

            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table_renegotiation_campaign.query(**query_params)

            # Add items if any exist
            if response.get('Count', 0) > 0:
                campaign_items.extend(response['Items'])

            # Check if there are more pages
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return campaign_items

    def list_active_campaigns_for_company(self, company_id: str, customer_ids: Optional[list] = None):
        filter_expression = Attr('is_active').eq(True)
        if customer_ids:
            customer_filter = None
            for v in customer_ids:
                cond = Attr('customer_ids').contains(v)
                customer_filter = cond if customer_filter is None else customer_filter | cond

            filter_expression = filter_expression & customer_filter

        response = self.table_renegotiation_campaign.query(
            IndexName='company_id',
            KeyConditionExpression=Key('company_id').eq(company_id),
            FilterExpression=filter_expression
        )

        campaigns = []
        for renegotiation_data in response['Items']:
            campaigns.append(
                RenegotiationCampaign(**renegotiation_data)
            )

        logger.info(f"Company ID : {company_id} - Len Active campaigns : {len(campaigns)}")
        if campaigns:
            campaigns.sort(key=lambda x: x.created_at)
        return campaigns

    def get_active_campaign_for_company(self, company_id: str, customer_ids: Optional[list] = None):
        campaigns = self.list_active_campaigns_for_company(company_id, customer_ids)
        if campaigns:
            return campaigns[0]


    def list_company_renegotiation_campaigns_by_end_date(self, company_id: str, end_date: str):
        try:
            query = {
                "IndexName": 'company_id',
                "KeyConditionExpression": 'company_id = :company_id',
                "FilterExpression": 'attribute_exists(end_date) AND attribute_type(end_date, :type_s) AND end_date <> :empty AND end_date <= :end_date',
                "ExpressionAttributeValues": {
                    ':company_id': company_id,
                    ':end_date': end_date,
                    ':empty': '',
                    ':type_s': 'S',
                },
            }

            last_evaluated_key = ""
            while last_evaluated_key is not None:
                if last_evaluated_key != "":
                    query["ExclusiveStartKey"] = last_evaluated_key

                response = self.table_renegotiation_campaign.query(**query)
                last_evaluated_key = response.get("LastEvaluatedKey", None)

                for item in response.get("Items"):
                    yield RenegotiationCampaign(**item)

        except Exception as ex:
            logger.exception(f'Problems listing campaigns from company {company_id} by end date {end_date}')
            raise ex