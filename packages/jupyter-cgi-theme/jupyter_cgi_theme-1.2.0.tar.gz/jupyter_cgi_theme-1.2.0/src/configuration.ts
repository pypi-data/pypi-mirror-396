export type Links = Array<{ label: string; href: string }>;

export type AppConfig = {
  appName: string;
  header: {
    isVisible: boolean;
    insulaAppsMenuLinks?: Links;
    otherInfoMenuLinks?: Links;
  };
};

export const appConfig: AppConfig = {
  appName: 'Insula Experiment',
  header: {
    isVisible: true
    // insulaAppsMenuLinks: [
    //   {
    //     label: 'Awareness',
    //     href: '<Awareness_link>'
    //   },
    //   {
    //     label: 'Intellect',
    //     href: '<Intellect_link>'
    //   },
    //   {
    //     label: 'Perception',
    //     href: '<Perception_link>'
    //   }
    // ]
    // otherInfoMenuLinks: [
    //   {
    //     label: 'Docs',
    //     href: '<Docs_link>'
    //   },
    //   {
    //     label: 'Support',
    //     href: '<Support_link>'
    //   }
    // ]
  }
};
