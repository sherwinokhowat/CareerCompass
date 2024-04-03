from __future__ import annotations
from typing import Any, Optional
from random import randint
import requests
import time
import csv
import math
import asyncio
import aiohttp
import json
from utility import clear_csv, write_csv, sanitize_details


async def process_job_listings(
    jobs: list, ids: set[int]
) -> None:  # this goes to scrape file
    """
    Handles the list of jobs past as the argument, i.e., parses more
    detailed information from each job, then ultimately stores it in a csv file.

    Note that the paramter 'jobs' is a list of 30 jobs and their information, retrieved from the GraphQL query.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_job_details(
                session, int(job["jobview"]["jobListingAdminDetails"]["jobListingId"])
            )
            for job in jobs
        ]
        responses = await asyncio.gather(*tasks)

        for i in range(len(jobs)):
            job = jobs[i]
            job_specifics = responses[i]
            if job_specifics == {}:
                continue

            job_title = job["jobview"]["header"]["jobTitleText"]
            employer_name = job["jobview"]["header"]["employerNameFromSearch"]
            rating = job["jobview"]["header"]["rating"]
            link = job["jobview"]["header"]["seoJobLink"]
            fragmented_desc = job["jobview"]["job"]["descriptionFragments"]
            job_id = job["jobview"]["jobListingAdminDetails"]["jobListingId"]
            if job_id in ids:  # prevents duplicates
                continue
            skills = job_specifics["header"]["indeedJobAttribute"]["skillsLabel"]
            latitutde = job_specifics["map"]["lat"]
            longitude = job_specifics["map"]["lng"]
            city = job_specifics["map"]["cityName"]
            country = job_specifics["map"]["country"]
            full_desc = job_specifics["job"]["description"]
            ids.add(job_id)  #

            if job["jobview"]["header"]["payPeriod"] is not None:
                pay_period = job["jobview"]["header"]["payPeriod"]
                pay = job["jobview"]["header"]["payPeriodAdjustedPay"]["p50"]
            else:
                pay = randint(40000, 50000)
                pay_period = "ANNUAL"

            if not rating:
                rating = "0"

            if latitutde is None or not latitutde:
                latitutde = -3.14159
            if longitude is None or not longitude:
                longitude = -3.14159
            if not country:
                currency = job["jobview"]["header"]["payCurrency"]
                if currency == "CAD":
                    country = "Canada"
                else:
                    country = "United States"

            job_details = [
                job_title,
                employer_name,
                rating,
                link,
                fragmented_desc,
                skills,
                latitutde,
                longitude,
                city,
                country,
                pay_period,
                pay,
                job_id,
                full_desc,
            ]
            sanitize_details(job_details)
            write_csv("jobs.csv", job_details)


async def fetch_job_details(session: aiohttp.ClientSession, job_id: int) -> dict:
    """
    Returns a dictionary filled with detailed information of the job associated with <job_id>.

    Note that <job_id> is unique, and Glassdoor's unique id for a job.
    """
    URL = "https://www.glassdoor.ca/graph"
    HEADERS = {
        "content-type": "application/json",
        "gd-csrf-token": "g1Pap2CLYOr1TlDIB7v_1w:BVvkWc1Czkiaae7GSEeK72VaaOmeSnPiMoU5Fv5z-J6bZkVxUHOBZ6o2lxrOBW362CjJXZhj5oHDq2uFnyq8tA:TaaIXLlfr3qKo1E8EYjcg5mMXgl99BTp8s-c4hq1Lp0",
        "User-Agent": "",
    }
    job_query = f'[{{"operationName":"JobDetailQuery","variables":{{"enableReviewSummary":true,"jl":{job_id},"queryString":"pos=103&ao=1136043&s=58&guid=0000018e8d41a5119fabc43362077072&src=GD_JOB_AD&t=SR&vt=w&ea=1&cs=1_0b675c31&cb=1711766873784&jobListingId=1009198443079&jrtk=5-yul1-0-1hq6k39a8hdh9802-1de3e23b19ddcb90","pageTypeEnum":"SERP"}},"query":"query JobDetailQuery($jl: Long!, $queryString: String, $enableReviewSummary: Boolean!, $pageTypeEnum: PageTypeEnum) {{\\n  jobview: jobView(\\n    listingId: $jl\\n    contextHolder: {{queryString: $queryString, pageTypeEnum: $pageTypeEnum}}\\n  ) {{\\n    ...DetailFragment\\n    employerReviewSummary @include(if: $enableReviewSummary) {{\\n      reviewSummary {{\\n        highlightSummary {{\\n          sentiment\\n          sentence\\n          categoryReviewCount\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n\\nfragment DetailFragment on JobView {{\\n  employerBenefits {{\\n    benefitsOverview {{\\n      benefitsHighlights {{\\n        benefit {{\\n          commentCount\\n          icon\\n          name\\n          __typename\\n        }}\\n        highlightPhrase\\n        __typename\\n      }}\\n      overallBenefitRating\\n      employerBenefitSummary {{\\n        comment\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    benefitReviews {{\\n      benefitComments {{\\n        id\\n        comment\\n        __typename\\n      }}\\n      cityName\\n      createDate\\n      currentJob\\n      rating\\n      stateName\\n      userEnteredJobTitle\\n      __typename\\n    }}\\n    numReviews\\n    __typename\\n  }}\\n  employerContent {{\\n    featuredVideoLink\\n    managedContent {{\\n      id\\n      type\\n      title\\n      body\\n      captions\\n      photos\\n      videos\\n      __typename\\n    }}\\n    diversityContent {{\\n      goals {{\\n        id\\n        workPopulation\\n        underRepresentedGroup\\n        currentMetrics\\n        currentMetricsDate\\n        representationGoalMetrics\\n        representationGoalMetricsDate\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  employerAttributes {{\\n    attributes {{\\n      attributeName\\n      attributeValue\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  gaTrackerData {{\\n    jobViewDisplayTimeMillis\\n    requiresTracking\\n    pageRequestGuid\\n    searchTypeCode\\n    trackingUrl\\n    __typename\\n  }}\\n  header {{\\n    jobLink\\n    adOrderId\\n    advertiserType\\n    ageInDays\\n    applicationId\\n    appliedDate\\n    applyUrl\\n    applyButtonDisabled\\n    blur\\n    coverPhoto {{\\n      url\\n      __typename\\n    }}\\n    divisionEmployerName\\n    easyApply\\n    easyApplyMethod\\n    employerNameFromSearch\\n    employer {{\\n      activeStatus\\n      bestProfile {{\\n        id\\n        __typename\\n      }}\\n      id\\n      name\\n      shortName\\n      size\\n      squareLogoUrl\\n      __typename\\n    }}\\n    expired\\n    goc\\n    hideCEOInfo\\n    indeedApplyMetadata\\n    indeedJobAttribute {{\\n      education\\n      skills\\n      educationLabel\\n      skillsLabel\\n      yearsOfExperienceLabel\\n      __typename\\n    }}\\n    isIndexableJobViewPage\\n    isSponsoredJob\\n    isSponsoredEmployer\\n    jobTitleText\\n    jobType\\n    jobTypeKeys\\n    jobCountryId\\n    jobResultTrackingKey\\n    locId\\n    locationName\\n    locationType\\n    needsCommission\\n    normalizedJobTitle\\n    organic\\n    payCurrency\\n    payPeriod\\n    payPeriodAdjustedPay {{\\n      p10\\n      p50\\n      p90\\n      __typename\\n    }}\\n    rating\\n    remoteWorkTypes\\n    salarySource\\n    savedJobId\\n    seoJobLink\\n    serpUrlForJobListing\\n    sgocId\\n    categoryMgocId\\n    urgencySignal {{\\n      labelKey\\n      messageKey\\n      normalizedCount\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  similarJobs {{\\n    relatedJobTitle\\n    careerUrl\\n    __typename\\n  }}\\n  job {{\\n    description\\n    discoverDate\\n    eolHashCode\\n    importConfigId\\n    jobReqId\\n    jobSource\\n    jobTitleId\\n    jobTitleText\\n    listingId\\n    __typename\\n  }}\\n  jobListingAdminDetails {{\\n    adOrderId\\n    cpcVal\\n    importConfigId\\n    jobListingId\\n    jobSourceId\\n    userEligibleForAdminJobDetails\\n    __typename\\n  }}\\n  map {{\\n    address\\n    cityName\\n    country\\n    employer {{\\n      id\\n      name\\n      __typename\\n    }}\\n    lat\\n    lng\\n    locationName\\n    postalCode\\n    stateName\\n    __typename\\n  }}\\n  overview {{\\n    ceo {{\\n      name\\n      photoUrl\\n      __typename\\n    }}\\n    id\\n    name\\n    shortName\\n    squareLogoUrl\\n    headquarters\\n    links {{\\n      overviewUrl\\n      benefitsUrl\\n      photosUrl\\n      reviewsUrl\\n      salariesUrl\\n      __typename\\n    }}\\n    primaryIndustry {{\\n      industryId\\n      industryName\\n      sectorName\\n      sectorId\\n      __typename\\n    }}\\n    ratings {{\\n      overallRating\\n      ceoRating\\n      ceoRatingsCount\\n      recommendToFriendRating\\n      compensationAndBenefitsRating\\n      cultureAndValuesRating\\n      careerOpportunitiesRating\\n      seniorManagementRating\\n      workLifeBalanceRating\\n      __typename\\n    }}\\n    revenue\\n    size\\n    sizeCategory\\n    type\\n    website\\n    yearFounded\\n    __typename\\n  }}\\n  photos {{\\n    photos {{\\n      caption\\n      photoId\\n      photoId2x\\n      photoLink\\n      photoUrl\\n      photoUrl2x\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  reviews {{\\n    reviews {{\\n      advice\\n      cons\\n      countHelpful\\n      employerResponses {{\\n        response\\n        responseDateTime\\n        userJobTitle\\n        __typename\\n      }}\\n      employmentStatus\\n      featured\\n      isCurrentJob\\n      jobTitle {{\\n        text\\n        __typename\\n      }}\\n      lengthOfEmployment\\n      pros\\n      ratingBusinessOutlook\\n      ratingCareerOpportunities\\n      ratingCeo\\n      ratingCompensationAndBenefits\\n      ratingCultureAndValues\\n      ratingOverall\\n      ratingRecommendToFriend\\n      ratingSeniorLeadership\\n      ratingWorkLifeBalance\\n      reviewDateTime\\n      reviewId\\n      summary\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  __typename\\n}}\\n"}}]'
    async with session.post(
        URL, headers=HEADERS, data=job_query, ssl=False
    ) as response:
        data = await response.text()
        # print(1, data)
        if response.status >= 300:
            time.sleep(0.1)
            print(response.status)
            return fetch_job_details(session, job_id)
        data = json.loads(data)
        return data[0]["data"]["jobview"]


# ====================================================================================
# Syncronuous Scraping Funcitons
# ====================================================================================


def scrape_us_jobs(ids: set[int]) -> None:
    """
    Scrape Glassdoor for every software internship job listings in the US.

    <fetch_jobs_us> is called with the respective pagination cursor, which returns a dictionary
    of 30 jobs and their generalized info. The next pagination cursor is then parsed (if there
    is one), and <process_job_listings> is called to parse and store the relevant details.

    Note that the function will continue scraping jobs until there are no more pagination cursors
    left (i.e., no more jobs).
    """
    clear_csv("jobs.csv")
    cursor = "AB4AAIEAAAAAAAAAAAAAAAAAAiR3vUAAAwAAAQAA"  # initial cursor

    page_number = 1
    tries = 0
    print("Gathering jobs... this might take a while!")
    while True and tries < 3:
        found = False
        job_list_data = fetch_jobs_us(cursor)

        paginations = job_list_data["paginationCursors"]
        jobs = job_list_data["jobListings"]  # this is the 30 jobs

        asyncio.run(process_job_listings(jobs, ids))
        time.sleep(0.15)
        for pagination in paginations:  # find the next cursor.
            if (
                pagination["pageNumber"] > page_number
            ):  # The first one should be the next one
                page_number += 1
                cursor = pagination["cursor"]
                found = True
                tries = 0
                break
        if not found:
            tries += 1
            time.sleep(3)
    print("Done US!")


def scrape_ca_jobs(ids: set[int]) -> None:
    """
    Scrape Glassdoor for every software internship job listings in Canada.

    <fetch_jobs_ca> is called with the respective pagination cursor, which returns a dictionary
    of 30 jobs and their generalized info. The next pagination cursor is then parsed (if there
    is one), and <process_job_listings> is called to parse and store the relevant details.

    Note that the function will continue scraping jobs until there are no more pagination cursors
    left (i.e., no more jobs).
    """
    cursor = "AB4AAIEAAAAAAAAAAAAAAAAAAiUV1vYAAwAAAQAA"  # initial cursor

    page_number = 1
    tries = 0
    print("Gathering jobs... this might take a while!")
    while True and tries < 3:
        found = False
        job_list_data = fetch_jobs_ca(cursor)

        paginations = job_list_data["paginationCursors"]
        jobs = job_list_data["jobListings"]  # this is the 30 jobs

        asyncio.run(process_job_listings(jobs, ids))
        time.sleep(0.15)
        for pagination in paginations:  # find the next cursor.
            if (
                pagination["pageNumber"] > page_number
            ):  # The first one should be the next one
                page_number += 1
                cursor = pagination["cursor"]
                found = True
                tries = 0
                break
        if not found:
            tries += 1
            time.sleep(3)
    print("Done CA!")


# ====================================================================================
# Fetch Functions
# ====================================================================================


def fetch_jobs_us(cursor: str) -> dict:
    """
    Returns a dictionary of 30 jobs with their generalized info.

    Cursor is the pagination cursor for the current query.
    """
    URL = "https://www.glassdoor.ca/graph"
    HEADERS = {
        "content-type": "application/json",
        "gd-csrf-token": "g1Pap2CLYOr1TlDIB7v_1w:BVvkWc1Czkiaae7GSEeK72VaaOmeSnPiMoU5Fv5z-J6bZkVxUHOBZ6o2lxrOBW362CjJXZhj5oHDq2uFnyq8tA:TaaIXLlfr3qKo1E8EYjcg5mMXgl99BTp8s-c4hq1Lp0",
        "User-Agent": "",
    }
    job_list_query = f'[{{"operationName":"uilTrackingMutation","variables":{{"events":[{{"eventType":"JOB_SEEN","jobTrackingKeys":["5-yul1-0-1hpneooe7iqsp800-57ba39f093e850ef"],"jobCountryId":1,"pageType":"SERP"}}]}},"query":"mutation uilTrackingMutation($events: [EventContextInput]!) {{\\n  trackEvents(events: $events) {{\\n    eventType\\n    resultStatus\\n    message\\n    clickId\\n    clickGuid\\n    __typename\\n  }}\\n}}\\n"}},{{"operationName":"JobSearchResultsQuery","variables":{{"excludeJobListingIds":[],"filterParams":[],"keyword":"software internship","locationId":1,"locationType":"COUNTRY","numJobsToShow":30,"originalPageUrl":"https://www.glassdoor.ca/Job/united-states-software-internship-jobs-SRCH_IL.0,13_IN1_KO14,33.htm","parameterUrlInput":"IL.0,13_IN1_KO14,33","pageType":"SERP","queryString":"","seoFriendlyUrlInput":"united-states-software-internship-jobs","seoUrl":true,"pageCursor":"{cursor}","pageNumber":1}},"query":"query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean) {{\\n  jobListings(\\n    contextHolder: {{queryString: $queryString, pageTypeEnum: $pageType, searchParams: {{excludeJobListingIds: $excludeJobListingIds, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, filterParams: $filterParams, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR}}}}\\n  ) {{\\n    companyFilterOptions {{\\n      id\\n      shortName\\n      __typename\\n    }}\\n    filterOptions\\n    indeedCtk\\n    jobListings {{\\n      ...JobView\\n      __typename\\n    }}\\n    jobListingSeoLinks {{\\n      linkItems {{\\n        position\\n        url\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    jobSearchTrackingKey\\n    jobsPageSeoData {{\\n      pageMetaDescription\\n      pageTitle\\n      __typename\\n    }}\\n    paginationCursors {{\\n      cursor\\n      pageNumber\\n      __typename\\n    }}\\n    indexablePageForSeo\\n    searchResultsMetadata {{\\n      searchCriteria {{\\n        implicitLocation {{\\n          id\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        keyword\\n        location {{\\n          id\\n          shortName\\n          localizedShortName\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      footerVO {{\\n        countryMenu {{\\n          childNavigationLinks {{\\n            id\\n            link\\n            textKey\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      helpCenterDomain\\n      helpCenterLocale\\n      jobAlert {{\\n        jobAlertExists\\n        __typename\\n      }}\\n      jobSerpFaq {{\\n        questions {{\\n          answer\\n          question\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      jobSerpJobOutlook {{\\n        occupation\\n        paragraph\\n        heading\\n        __typename\\n      }}\\n      showMachineReadableJobs\\n      __typename\\n    }}\\n    serpSeoLinksVO {{\\n      relatedJobTitlesResults\\n      searchedJobTitle\\n      searchedKeyword\\n      searchedLocationIdAsString\\n      searchedLocationSeoName\\n      searchedLocationType\\n      topCityIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerNameResults\\n      topOccupationResults\\n      __typename\\n    }}\\n    totalJobsCount\\n    __typename\\n  }}\\n}}\\n\\nfragment JobView on JobListingSearchResult {{\\n  jobview {{\\n    header {{\\n      adOrderId\\n      advertiserType\\n      ageInDays\\n      divisionEmployerName\\n      easyApply\\n      employer {{\\n        id\\n        name\\n        shortName\\n        __typename\\n      }}\\n      organic\\n      employerNameFromSearch\\n      goc\\n      gocConfidence\\n      gocId\\n      isSponsoredJob\\n      isSponsoredEmployer\\n      jobCountryId\\n      jobLink\\n      jobResultTrackingKey\\n      normalizedJobTitle\\n      jobTitleText\\n      locationName\\n      locationType\\n      locId\\n      needsCommission\\n      payCurrency\\n      payPeriod\\n      payPeriodAdjustedPay {{\\n        p10\\n        p50\\n        p90\\n        __typename\\n      }}\\n      rating\\n      salarySource\\n      savedJobId\\n      seoJobLink\\n      __typename\\n    }}\\n    job {{\\n      descriptionFragments\\n      importConfigId\\n      jobTitleId\\n      jobTitleText\\n      listingId\\n      __typename\\n    }}\\n    jobListingAdminDetails {{\\n      cpcVal\\n      importConfigId\\n      jobListingId\\n      jobSourceId\\n      userEligibleForAdminJobDetails\\n      __typename\\n    }}\\n    overview {{\\n      shortName\\n      squareLogoUrl\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  __typename\\n}}\\n"}}]'
    response = requests.post(URL, headers=HEADERS, data=job_list_query)
    if response:
        return response.json()[1]["data"]["jobListings"]
    else:
        print("\n\n\n")
        print(f"HTTP Response: {response.status_code}\n Try again later.")
        quit()


def fetch_jobs_ca(cursor: str) -> dict:
    """
    Returns a dictionary of 30 jobs with their generalized info.

    Cursor is the pagination cursor for the current query.
    """
    URL = "https://www.glassdoor.ca/graph"
    HEADERS = {
        "content-type": "application/json",
        "gd-csrf-token": "g1Pap2CLYOr1TlDIB7v_1w:BVvkWc1Czkiaae7GSEeK72VaaOmeSnPiMoU5Fv5z-J6bZkVxUHOBZ6o2lxrOBW362CjJXZhj5oHDq2uFnyq8tA:TaaIXLlfr3qKo1E8EYjcg5mMXgl99BTp8s-c4hq1Lp0",
        "User-Agent": "",
    }
    job_list_query = f'[{{"operationName":"JobSearchResultsQuery","variables":{{"excludeJobListingIds":[],"filterParams":[],"keyword":"software internship","locationId":3,"locationType":"COUNTRY","numJobsToShow":30,"originalPageUrl":"https://www.glassdoor.ca/Job/canada-software-internship-jobs-SRCH_IL.0,6_IN3_KO7,26.htm","parameterUrlInput":"IL.0,6_IN3_KO7,26","pageType":"SERP","queryString":"","seoFriendlyUrlInput":"canada-software-internship-jobs","seoUrl":true,"includeIndeedJobAttributes":true,"pageCursor":"{cursor}","pageNumber":2}},"query":"query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean, $includeIndeedJobAttributes: Boolean) {{\\n  jobListings(\\n    contextHolder: {{queryString: $queryString, pageTypeEnum: $pageType, searchParams: {{excludeJobListingIds: $excludeJobListingIds, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, filterParams: $filterParams, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR, includeIndeedJobAttributes: $includeIndeedJobAttributes}}}}\\n  ) {{\\n    companyFilterOptions {{\\n      id\\n      shortName\\n      __typename\\n    }}\\n    filterOptions\\n    indeedCtk\\n    jobListings {{\\n      ...JobView\\n      __typename\\n    }}\\n    jobListingSeoLinks {{\\n      linkItems {{\\n        position\\n        url\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    jobSearchTrackingKey\\n    jobsPageSeoData {{\\n      pageMetaDescription\\n      pageTitle\\n      __typename\\n    }}\\n    paginationCursors {{\\n      cursor\\n      pageNumber\\n      __typename\\n    }}\\n    indexablePageForSeo\\n    searchResultsMetadata {{\\n      searchCriteria {{\\n        implicitLocation {{\\n          id\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        keyword\\n        location {{\\n          id\\n          shortName\\n          localizedShortName\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      footerVO {{\\n        countryMenu {{\\n          childNavigationLinks {{\\n            id\\n            link\\n            textKey\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      helpCenterDomain\\n      helpCenterLocale\\n      jobAlert {{\\n        jobAlertExists\\n        __typename\\n      }}\\n      jobSerpFaq {{\\n        questions {{\\n          answer\\n          question\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      jobSerpJobOutlook {{\\n        occupation\\n        paragraph\\n        heading\\n        __typename\\n      }}\\n      showMachineReadableJobs\\n      __typename\\n    }}\\n    serpSeoLinksVO {{\\n      relatedJobTitlesResults\\n      searchedJobTitle\\n      searchedKeyword\\n      searchedLocationIdAsString\\n      searchedLocationSeoName\\n      searchedLocationType\\n      topCityIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerNameResults\\n      topOccupationResults\\n      __typename\\n    }}\\n    totalJobsCount\\n    __typename\\n }}\\n}}\\n\\nfragment JobView on JobListingSearchResult {{\\n  jobview {{\\n    header {{\\n      indeedJobAttribute {{\\n        skills\\n        extractedJobAttributes {{\\n          key\\n          value\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      adOrderId\\n      advertiserType\\n      ageInDays\\n      divisionEmployerName\\n      easyApply\\n      employer {{\\n        id\\n        name\\n        shortName\\n        __typename\\n      }}\\n      organic\\n      employerNameFromSearch\\n      goc\\n      gocConfidence\\n      gocId\\n      isSponsoredJob\\n      isSponsoredEmployer\\n      jobCountryId\\n      jobLink\\n      jobResultTrackingKey\\n      normalizedJobTitle\\n      jobTitleText\\n      locationName\\n      locationType\\n      locId\\n      needsCommission\\n      payCurrency\\n      payPeriod\\n      payPeriodAdjustedPay {{\\n        p10\\n        p50\\n        p90\\n        __typename\\n      }}\\n      rating\\n      salarySource\\n      savedJobId\\n      seoJobLink\\n      __typename\\n    }}\\n    job {{\\n      descriptionFragments\\n      importConfigId\\n      jobTitleId\\n      jobTitleText\\n      listingId\\n      __typename\\n    }}\\n    jobListingAdminDetails {{\\n      cpcVal\\n      importConfigId\\n      jobListingId\\n      jobSourceId\\n      userEligibleForAdminJobDetails\\n      __typename\\n    }}\\n    overview {{\\n      shortName\\n      squareLogoUrl\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  __typename\\n}}\\n"}}]'
    response = requests.post(URL, headers=HEADERS, data=job_list_query)
    if response:
        return response.json()[0]["data"]["jobListings"]
    else:
        print("\n\n\n")
        print(f"HTTP Response: {response.status_code}\n Try again later.")
        quit()


# ====================================================================================
# Scraper
# ====================================================================================


def scrape() -> None:
    """
    Scrapes and stores all available software internships available
    located in Canada and the US on Glassdoor.
    """
    ids = set()
    scrape_us_jobs(ids)
    scrape_ca_jobs(ids)


# ====================================================================================
# Main Function
# ====================================================================================


if __name__ == "__main__":
    scrape()
