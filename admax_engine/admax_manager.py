import uuid
import logging

from leaf_engine.models import *
from user_engine.backends import EdenSessionManagement 
from leaf_engine.leaf_management import EdenLeafManagement
from admax_engine.models import Advertisements, AdvertisementCampaigns, PromotedLeafs



session_management_object = EdenSessionManagement()
leaf_management_object = EdenLeafManagement()


class Eden_ADMAX_Engine():
    
    def meta(self):
        self.VERSION = 0.5
        self.MAX_OBJECT_LIMIT = 50
    
    def __init__(self) -> None:
        self.meta()
        logging.info(f"Eden_ADMAX_Engine {self.VERSION}")
    
    def generate_campaign_id(self):
        return str(uuid.uuid4()).upper().replace("-", "")
    
    def create_advertisement_campaign(self,request, data):
        user_object = data['user_object']
        campaign_name = data['campaign_name']
        campaign_object = AdvertisementCampaigns()
        try:
            if self.is_authorised(request):
                campaign_object.campaign_id = self.generate_campaign_id()
                campaign_object.created_by = user_object
                campaign_object.campaign_name = campaign_name
                campaign_object.save()
                return -100
            else:
                return -122
        except Exception as e:
            return -111

    def create_advertisement_instance(self,request,data):
        data['leaf_type'] = LeafType.Public
        if len(data['text_content'].strip()) < 1:
            return {'status':200, 'message': f"Text content is empty"}
        leaf_creation_response = leaf_management_object.create_leaf(request,data)
        leaf_id = leaf_creation_response['leaf_id']
        try:
            campaign_instance = self.fetch_campaign_instance(data['campaign_id'])
            if self.is_authorised(request) and campaign_instance is not None:
                leaf_object = leaf_management_object.get_leaf_object(leaf_id)
                advertisement_obj = Advertisements()
                advertisement_obj.advertisement_id = self.generate_campaign_id()
                advertisement_obj.leaf = leaf_object
                advertisement_obj.created_by = leaf_management_object.get_user_object(user_id=data['user_id'])
                #advertisement_obj.target_topic_id = data['target_topic_id']
                advertisement_obj.target_topic_category = data['target_topic_category_id']
                advertisement_obj.advertisement_tier = data['advertisement_tier']

                advertisement_obj.campaign = campaign_instance
                advertisement_obj.is_active = True
                
                advertisement_obj.save()

                campaign_instance.active_ads += 1
                campaign_instance.total_ads += 1
                campaign_instance.save()
                return {'status':200, 'message': f"Advertisement is active."}
            else:
                leaf_management_object.delete_leaf(request,leaf_id)
                return {'status':200, 'message': f"User not authorised. or Campaign doesnot exists {self.fetch_campaign_instance(data['campaign_id'])}"}
                
        except Exception as e:
            leaf_management_object.delete_leaf(request,leaf_id)
            return {'status':200, 'message': f"Advertisement could not be created. {e}"}
        
    
    def fetch_advertisement_instance(self, user_object, leaf):
        try:
            return Advertisements.objects.filter(created_by = user_object, leaf= leaf).get()
        except Exception as e:
            raise e
    
    def fetch_campaign_instance(self, campaign_id):
        try:
            return AdvertisementCampaigns.objects.filter(campaign_id=campaign_id ).get()
        except Exception as e:
            raise e

    def get_campaign_id(self, campaign_name, user_id):
        try:

            return AdvertisementCampaigns.objects.filter(campaign_name= campaign_name, 
                                                        created_by= leaf_management_object.get_user_object(user_id)).first().campaign_id
        except Exception as e:
            raise e
    def get_advertisement_object_with_id(self,advertisement_id):
        return Advertisements.objects.filter(advertisement_id= advertisement_id).first()
    
    def delete_ad(self,request,advertisement_id): 
        try:
            advertisement_obj = self.get_advertisement_object_with_id(advertisement_id)
            if advertisement_id is not None:
                leaf_management_object.delete_leaf(request,advertisement_obj)
                advertisement_obj.delete()
                return  {'status':200, 'message': f"Advertisement deleted."}

        except Exception as e:
            return {'status': 200, 'message': f'Error occurred - {e}'}

    def delete_campaign(self, request,data):
        try:
            campaign_id = data['campaign_id']
            logged_in_user = leaf_management_object.get_logged_in_user(request)
            campaign_instance = self.fetch_campaign_instance(campaign_id)
            if campaign_instance.created_by == logged_in_user:
                advertisements_query_set = Advertisements.objects.filter(campaign = campaign_instance).all()
                for ad in advertisements_query_set:
                    leaf_management_object.delete_leaf(request, ad.leaf.leaf_id)
                    ad.delete()
                campaign_instance.delete()
                return -100
            else:
                return -141
        except Exception as e:
            raise e
            return -111

    def check_leaf_ad_exists(self,data):
        try:
            leaf_id = data['leaf_id']
            leaf_object = leaf_management_object.get_leaf_object(leaf_id)
            return leaf_object is not None and leaf_object.is_advertisement == True
        except:
            return False
    
    def get_ad_analytics(self, leaf_id):
        leaf_object = leaf_management_object.get_leaf_object(leaf_id)
        return self.leaf_to_json(leaf_object)
    
    def get_campaign_summary(self, campaign_id):
        try:
            campaign_instance = self.fetch_campaign_instance(campaign_id)
            advertisement_query_set = Advertisements.objects.filter(campaign = campaign_instance, is_active = True).values('leaf')
            leaf_query_set = Leaf.objects.filter(leaf_id__in = advertisement_query_set).values('leaf_id', 'comments_count', 'likes_count', 
                                                                                               'dislikes_count', 'engagement_rating', 
                                                                                              'view_count')
            total_likes_count = 0
            total_dislikes_count = 0
            total_comments_count = 0
            total_views_count = 0
            total_leaves = 0
            total_engagement_rating = 0
            for leaf in leaf_query_set:
                total_likes_count += leaf.likes_count
                total_dislikes_count += leaf.dislikes_count
                total_comments_count += leaf.comments_count
                total_views_count += leaf.view_count
                total_engagement_rating += leaf.engagement_rating
                total_leaves += 1
            
            avg_engagement_rating = total_engagement_rating / total_leaves

            return {
                'campaign_name': campaign_instance.campaign_name,
                'total_ads': campaign_instance.total_ads,
                'total_active_ads': campaign_instance.active_ads,
                'total_likes': total_likes_count,
                'total_dislikes': total_dislikes_count,
                'total_comments_count': total_comments_count,
                'total_views_count': total_views_count,
                'average_engagement_rating': avg_engagement_rating
            }
        except:
            return -111
    
    def stream_ads_topic_wise(self,topic_id):
        return Advertisements.objects.filter(target_topic_id__contains = topic_id).order_by('-advertisement_tier').values('leaf')
    
    
    def stream_ads_topic_category_wise(self, topic_category):
        return Advertisements.objects.filter(target_topic_category__contains = topic_category).order_by('-advertisement_tier').values('leaf')
    

    def fetch_promoted_instance(self, leaf):
        return PromotedLeafs.objects.filter(leaf= leaf).get()
    
    def create_promoted_leaf(self,request ,data):
        leaf_creation_response = leaf_management_object.create_leaf(request,data)
        try:
            leaf_id = leaf_creation_response['leaf_id']
            boost_multiplier = data['boost_multiplier']
            duration = data['duration']
            return self.make_leaf_into_promoted_leaf(leaf_id,boost_multiplier, duration )
        except:
            return -161
    
    def make_leaf_into_promoted_leaf(self,leaf_id, boost_multiplier, duration):
        leaf_object = leaf_management_object.get_leaf_object(leaf_id)
        if leaf_object is None:
            return -152
        try:
            promoted_instance = self.fetch_promoted_instance(leaf_object)
            if promoted_instance is None:
                new_promoted_instance = PromotedLeafs()
                new_promoted_instance.leaf = leaf_object
                new_promoted_instance.boost_multiplier = boost_multiplier
                new_promoted_instance.is_active = True
                new_promoted_instance.created_by = leaf_object.owner
                year, month, day = [int(i) for i in duration.split("-")]
                new_promoted_instance.expiry = datetime.datetime(year=year,month=month,day=day)
                leaf_object.is_promoted = True

                new_promoted_instance.save()
                leaf_object.save()
                return 100
            else:
                if boost_multiplier <= 1.2 and boost_multiplier > 1:
                    promoted_instance.boost_multiplier = boost_multiplier  - 0.2
                elif boost_multiplier > 1.2 and boost_multiplier < 2:
                    promoted_instance.boost_multiplier = boost_multiplier - 0.4
                elif boost_multiplier > 2:
                    promoted_instance.boost_multiplier = boost_multiplier - 0.6
                year, month, day = [int(i) for i in duration.split("-")]
                promoted_instance.expiry = datetime.datetime(year=year,month=month,day=day)
                promoted_instance.save()
                return 100
        except:
            return -151
    
    def remove_promoted_status(self,leaf_id):
        leaf_object = leaf_management_object.get_leaf_object(leaf_id)
        try:
            promoted_instance = self.fetch_promoted_instance(leaf_object)
            if promoted_instance is not None:
                promoted_instance.delete()
                leaf_object.is_promoted = False
                leaf_object.save()
                return 100
            else:
                return 151
        except:
            return 152
    
    def is_authorised(self, request) -> bool:
        return session_management_object.current_session(
            request
        ) != None and session_management_object.check_session(
            request.session["auth_token"]
        )

    def get_ad_summary(self, leaf_id):
        return self.leaf_to_json(leaf_object= leaf_management_object.get_leaf_object(leaf_id))

    def leaf_to_json(self, leaf_object):
        return {
            'created_date': str(leaf_object.created_date),
            'leaf_id': str(leaf_object.leaf_id),
            'likes_count': str(leaf_object.likes_count),
            'dislikes_count': str(leaf_object.dislikes_count),
            'comment_count': str(leaf_object.comments_count),
            'view_count': str(leaf_object.view_count),
            'engagement_rating': str(leaf_object.engagement_rating),
            'exp_points': str(leaf_object.exp_points),
            'leaf_topic_id': str(leaf_object.leaf_topic_id),
            'topic_category_id': str(leaf_object.leaf_topic_category_id),
            'leaf_emotion_state': str(leaf_object.leaf_emotion_state),
            'is_promoted': str(leaf_object.is_promoted),
            'is_advertisement': str(leaf_object.is_advertisement),
            'topic_relevancy_percentage':str(leaf_object.topic_relevenacy_percentage) ,
            'category_relevancy_percentage': str(leaf_object.category_relevenacy_percentage)
        }